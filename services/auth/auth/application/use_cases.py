"""Auth use cases — all business logic lives here, not in API routes.

Use cases receive dependencies via constructor injection.
They are instantiated by provider functions in infrastructure/dependencies.py.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sp.core.config import Settings
from sp.infrastructure.security.jwt import (
    create_tokens,
    create_verification_token,
    verify_verification_token,
)

from ..domain.exceptions import (
    GoogleTokenError,
    InvalidSessionError,
    InvalidVerificationTokenError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    UserAlreadyExistsError,
)
from ..domain.interfaces import (
    AccountRepositoryProtocol,
    GoogleTokenVerifierProtocol,
    OTPProviderProtocol,
    SessionRepositoryProtocol,
    UserRepositoryProtocol,
    VerificationRepositoryProtocol,
)
from ..domain.models import Account, Session, User, UserRole, Verification


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_session_and_tokens(
    user: User,
    session_id,
    settings: Settings,
    metadata: dict,
) -> tuple[Session, dict]:
    """Shared logic for creating a session + token pair."""
    tokens = create_tokens(
        user_id=user.id,
        email=user.email or "",
        role=user.role.value,
        session_id=session_id,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_minutes=settings.JWT_EXPIRATION_MINUTES,
    )
    session = Session(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=hashlib.sha256(
            tokens["refresh_token"].encode()
        ).hexdigest(),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        user_agent=metadata.get("user_agent"),
        ip_address=metadata.get("ip_address"),
    )
    return session, tokens


# ── OTP: Send ─────────────────────────────────────────────────────────────────


class SendOTPUseCase:
    """Generate and send a 6-digit OTP via WhatsApp."""

    def __init__(
        self,
        otp_provider: OTPProviderProtocol,
        verification_repo: VerificationRepositoryProtocol,
    ) -> None:
        self.otp_provider = otp_provider
        self.verification_repo = verification_repo

    async def execute(self, phone: str) -> None:
        code = f"{secrets.randbelow(900000) + 100000}"

        verification = Verification(
            id=uuid4(),
            identifier=phone,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

        await self.verification_repo.create(verification)
        await self.otp_provider.send_otp(phone, code)


# ── OTP: Verify (returns verification_token, does NOT create user) ────────────


class VerifyOTPUseCase:
    """Verify the OTP code → return a short-lived verification_token (proof of phone)."""

    def __init__(
        self,
        verification_repo: VerificationRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.verification_repo = verification_repo
        self.settings = settings

    async def execute(self, phone: str, otp_code: str) -> str:
        """Returns a verification_token JWT proving phone ownership."""
        verification = await self.verification_repo.find_valid(phone)
        if not verification:
            raise OTPExpiredError("OTP expired or not found")

        if verification.attempt_count >= verification.max_attempts:
            raise OTPMaxAttemptsError("Too many failed attempts. Request a new OTP.")

        incoming_hash = hashlib.sha256(otp_code.encode()).hexdigest()
        if verification.code_hash != incoming_hash:
            await self.verification_repo.increment_attempts(verification.id)
            raise OTPInvalidError("Invalid OTP code")

        await self.verification_repo.mark_verified(verification.id)

        return create_verification_token(
            phone=phone,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
        )


# ── Register (Phone-first Path A completion) ─────────────────────────────────


class RegisterUseCase:
    """Create a verified rider from a verification_token + profile data."""

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self, verification_token: str, full_name: str, metadata: dict
    ) -> dict:
        # 1. Decode verification_token → extract phone
        phone = verify_verification_token(
            verification_token,
            self.settings.JWT_SECRET,
            self.settings.JWT_ALGORITHM,
        )
        if not phone:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token"
            )

        # 2. Check phone isn't already registered
        existing = await self.user_repo.find_by_phone(phone)
        if existing:
            raise UserAlreadyExistsError("Phone number already registered")

        # 3. Create verified user
        user = await self.user_repo.save(
            User.create(
                role=UserRole.PASSENGER,
                full_name=full_name,
                phone=phone,
                is_verified=True,
            )
        )

        # 4. Create session + tokens
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)

        return tokens


# ── Google: Verify ID Token (Path B start) ────────────────────────────────────


class GoogleVerifyTokenUseCase:
    """Verify Google id_token → create unverified user + account → issue tokens."""

    def __init__(
        self,
        google_verifier: GoogleTokenVerifierProtocol,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.google_verifier = google_verifier
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(self, id_token_str: str, metadata: dict) -> dict:
        # 1. Verify the Google id_token
        try:
            claims = await self.google_verifier.verify(id_token_str)
        except Exception as e:
            raise GoogleTokenError(f"Google token verification failed: {e}")

        google_sub = claims["sub"]
        email = claims.get("email", "")
        name = claims.get("name", "")

        # 2. Check if this Google account already exists
        existing_account = await self.account_repo.find_by_provider(
            "google", google_sub
        )

        if existing_account:
            # Returning user — find their User and issue tokens
            user = await self.user_repo.find_by_id(existing_account.user_id)
            if not user:
                raise GoogleTokenError("Linked user not found")
        else:
            # New user — create User (unverified) + Account
            user = await self.user_repo.save(
                User.create(
                    role=UserRole.PASSENGER,
                    full_name=name,
                    email=email,
                    is_verified=False,  # not verified until phone is linked
                )
            )
            await self.account_repo.save(
                Account(
                    id=uuid4(),
                    user_id=user.id,
                    provider="google",
                    provider_account_id=google_sub,
                )
            )

        # 3. Create session + tokens
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)

        # 4. Signal to frontend whether phone verification is needed
        tokens["phone_required"] = not user.is_verified

        return tokens


# ── Google: Link Phone (Path B completion, with account merge) ────────────────


class LinkPhoneUseCase:
    """Link a verified phone to the authenticated Google user.

    Handles account merge: if the phone belongs to an existing phone-only user,
    migrates the Google Account to that user and deletes the temporary one.
    """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self,
        current_user_id,
        verification_token: str,
        metadata: dict,
    ) -> dict:
        # 1. Decode verification_token → extract phone
        phone = verify_verification_token(
            verification_token,
            self.settings.JWT_SECRET,
            self.settings.JWT_ALGORITHM,
        )
        if not phone:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token"
            )

        # 2. Load the current (Google-created) user
        current_user = await self.user_repo.find_by_id(current_user_id)
        if not current_user:
            raise InvalidSessionError("Current user not found")

        # 3. Check if this phone belongs to an existing user
        phone_owner = await self.user_repo.find_by_phone(phone)

        if phone_owner and phone_owner.id != current_user.id:
            # ── ACCOUNT MERGE ─────────────────────────────────────────
            # The phone belongs to an existing phone-only user.
            # Migrate Google account(s) from current_user → phone_owner.
            google_accounts = await self.account_repo.find_by_user_id(
                current_user.id
            )
            for account in google_accounts:
                await self.account_repo.transfer_to_user(
                    account.id, phone_owner.id
                )

            # Copy Google info to phone_owner if missing
            if not phone_owner.full_name and current_user.full_name:
                phone_owner.full_name = current_user.full_name
            if not phone_owner.email and current_user.email:
                phone_owner.email = current_user.email
            await self.user_repo.update(phone_owner)

            # Revoke all sessions for the temporary Google user
            await self.session_repo.revoke_all_for_user(current_user.id)

            # Delete the temporary Google user (cascade deletes sessions)
            await self.user_repo.delete(current_user.id)

            # The merged user is the phone_owner
            merged_user = phone_owner
        else:
            # ── SIMPLE LINK (no conflict) ─────────────────────────────
            current_user.phone = phone
            current_user.is_verified = True
            await self.user_repo.update(current_user)
            merged_user = current_user

        # 4. Create new session + tokens for the final user
        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            merged_user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)
        tokens["phone_required"] = False

        return tokens


# ── Token Refresh ─────────────────────────────────────────────────────────────


class RefreshTokenUseCase:
    """Rotate the refresh token and issue a new access token."""

    def __init__(
        self,
        session_repo: SessionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.settings = settings

    async def execute(self, old_refresh_token: str) -> dict:
        token_hash = hashlib.sha256(old_refresh_token.encode()).hexdigest()
        session = await self.session_repo.find_by_hash(token_hash)

        if not session or session.is_revoked:
            raise InvalidSessionError("Session not found or revoked")

        if session.expires_at < datetime.now(timezone.utc):
            raise InvalidSessionError("Session expired")

        user = await self.user_repo.find_by_id(session.user_id)
        if not user:
            raise InvalidSessionError("User not found")

        new_tokens = create_tokens(
            user_id=user.id,
            email=user.email or "",
            role=user.role.value,
            session_id=session.id,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
            access_ttl_minutes=self.settings.JWT_EXPIRATION_MINUTES,
        )

        session.refresh_token_hash = hashlib.sha256(
            new_tokens["refresh_token"].encode()
        ).hexdigest()
        session.last_active_at = datetime.now(timezone.utc)
        await self.session_repo.update(session)

        return new_tokens