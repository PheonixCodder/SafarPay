"""Auth use cases — all business logic lives here, not in API routes.

Use cases receive dependencies via constructor injection.
They are instantiated by provider functions in infrastructure/dependencies.py.
"""
from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
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

logger = logging.getLogger("auth.application")

GOOGLE_EXISTING_PHONE_PURPOSE = "google_existing_phone_login"


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


def _mask_phone(phone: str) -> str:
    return f"******{phone[-4:]}" if len(phone) >= 4 else "******"


def _create_google_existing_phone_token(
    *,
    user: User,
    phone: str,
    google_sub: str,
    email: str,
    settings: Settings,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "purpose": GOOGLE_EXISTING_PHONE_PURPOSE,
        "user_id": str(user.id),
        "phone": phone,
        "google_sub": google_sub,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _verify_google_existing_phone_token(
    token: str,
    settings: Settings,
) -> dict | None:
    try:
        raw = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        logger.debug("Google existing phone token failed: %s", exc)
        return None

    if raw.get("purpose") != GOOGLE_EXISTING_PHONE_PURPOSE:
        return None
    if not raw.get("user_id") or not raw.get("phone") or not raw.get("google_sub"):
        return None
    return raw


async def _create_and_send_otp(
    otp_provider: OTPProviderProtocol,
    verification_repo: VerificationRepositoryProtocol,
    phone: str,
) -> None:
    code = f"{secrets.randbelow(900000) + 100000}"
    verification = Verification(
        id=uuid4(),
        identifier=phone,
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    await verification_repo.create(verification)
    await otp_provider.send_otp(phone, code)


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
        await _create_and_send_otp(
            self.otp_provider,
            self.verification_repo,
            phone,
        )


# ── OTP: Verify (returns login or profile-completion next step) ───────────────


class VerifyOTPUseCase:
    """Verify the OTP code and return the next auth/profile step."""

    def __init__(
        self,
        verification_repo: VerificationRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.verification_repo = verification_repo
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self,
        phone: str,
        otp_code: str,
        metadata: dict,
        purpose: str = "phone_login",
    ) -> dict:
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

        registration_token = create_verification_token(
            phone=phone,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
        )

        if purpose == "phone_link":
            return {
                "next_step": "link_phone",
                "registration_token": registration_token,
            }

        existing_user = await self.user_repo.find_by_phone(phone)
        if not existing_user:
            return {
                "next_step": "complete_profile",
                "registration_token": registration_token,
            }

        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            existing_user,
            session_id,
            self.settings,
            metadata,
        )
        await self.session_repo.save(session)
        tokens["next_step"] = "login"
        tokens["phone_required"] = False

        return tokens


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
        self,
        verification_token: str,
        full_name: str,
        email: str,
        gender: str,
        date_of_birth: date,
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

        # 2. Check phone isn't already registered
        existing = await self.user_repo.find_by_phone(phone)
        if existing:
            raise UserAlreadyExistsError("Phone number already registered")

        existing_email = await self.user_repo.find_by_email(email)
        if existing_email:
            raise UserAlreadyExistsError("Email already registered")

        # 3. Create verified user
        user = await self.user_repo.save(
            User.create(
                role=UserRole.PASSENGER,
                full_name=full_name,
                email=email,
                phone=phone,
                gender=gender,
                date_of_birth=date_of_birth,
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


# ── Profile Update ────────────────────────────────────────────────────────────


class UpdateUserProfileUseCase:
    """Update editable user profile fields. Phone is intentionally immutable here."""

    def __init__(self, user_repo: UserRepositoryProtocol) -> None:
        self.user_repo = user_repo

    async def execute(
        self,
        user_id,
        full_name: str | None = None,
        email: str | None = None,
        gender: str | None = None,
        date_of_birth: date | None = None,
    ) -> User:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise InvalidSessionError("User not found")

        if email and email != user.email:
            existing = await self.user_repo.find_by_email(email)
            if existing and existing.id != user.id:
                raise UserAlreadyExistsError("Email already registered")
            user.email = email

        if full_name is not None:
            user.full_name = full_name
        if gender is not None:
            user.gender = gender
        if date_of_birth is not None:
            user.date_of_birth = date_of_birth

        return await self.user_repo.update(user)


# ── Google: Verify ID Token (Path B start) ────────────────────────────────────


class GoogleVerifyTokenUseCase:
    """Verify Google id_token → create unverified user + account → issue tokens."""

    def __init__(
        self,
        google_verifier: GoogleTokenVerifierProtocol,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        otp_provider: OTPProviderProtocol,
        verification_repo: VerificationRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.google_verifier = google_verifier
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.otp_provider = otp_provider
        self.verification_repo = verification_repo
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
        picture = claims.get("picture", "")

        # 2. Check if this Google account already exists
        existing_account = await self.account_repo.find_by_provider(
            "google", google_sub
        )

        if existing_account:
            # Returning linked Google user. Saved-phone accounts must still
            # prove phone ownership before app tokens are issued.
            user = await self.user_repo.find_by_id(existing_account.user_id)
            if not user:
                raise GoogleTokenError("Linked user not found")

            if email and user.email != email:
                email_owner = await self.user_repo.find_by_email(email)
                if email_owner and email_owner.id != user.id:
                    raise GoogleTokenError("Google email already belongs to another user")

                user.email = email
                user = await self.user_repo.update(user)
                logger.info(
                    "Google linked user email synced",
                    extra={
                        "user_id": str(user.id),
                        "provider_account_id": google_sub,
                    },
                )

            if user.phone:
                await _create_and_send_otp(
                    self.otp_provider,
                    self.verification_repo,
                    user.phone,
                )
                return {
                    "next_step": "verify_existing_phone",
                    "masked_phone": _mask_phone(user.phone),
                    "google_login_token": _create_google_existing_phone_token(
                        user=user,
                        phone=user.phone,
                        google_sub=google_sub,
                        email=email or user.email or "",
                        settings=self.settings,
                    ),
                    "phone_required": False,
                }
        else:
            email_owner = await self.user_repo.find_by_email(email) if email else None
            if email_owner and email_owner.phone:
                await _create_and_send_otp(
                    self.otp_provider,
                    self.verification_repo,
                    email_owner.phone,
                )
                return {
                    "next_step": "verify_existing_phone",
                    "masked_phone": _mask_phone(email_owner.phone),
                    "google_login_token": _create_google_existing_phone_token(
                        user=email_owner,
                        phone=email_owner.phone,
                        google_sub=google_sub,
                        email=email,
                        settings=self.settings,
                    ),
                    "phone_required": False,
                }

            if email_owner:
                user = email_owner
                if picture and not user.profile_img:
                    user.profile_img = picture
                if name and not user.full_name:
                    user.full_name = name
                user = await self.user_repo.update(user)
                await self.account_repo.save(
                    Account(
                        id=uuid4(),
                        user_id=user.id,
                        provider="google",
                        provider_account_id=google_sub,
                    )
                )
                session_id = uuid4()
                session, tokens = _build_session_and_tokens(
                    user, session_id, self.settings, metadata
                )
                await self.session_repo.save(session)
                tokens["phone_required"] = True
                return tokens
            # New user — create User (unverified) + Account
            user = await self.user_repo.save(
                User.create(
                    role=UserRole.PASSENGER,
                    full_name=name,
                    email=email,
                    profile_img=picture,
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


class VerifyGoogleExistingPhoneUseCase:
    """Verify OTP for a Google email that matches an existing phone user."""

    def __init__(
        self,
        verification_repo: VerificationRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        account_repo: AccountRepositoryProtocol,
        session_repo: SessionRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self.verification_repo = verification_repo
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.session_repo = session_repo
        self.settings = settings

    async def execute(
        self,
        google_login_token: str,
        otp_code: str,
        metadata: dict,
    ) -> dict:
        claims = _verify_google_existing_phone_token(
            google_login_token,
            self.settings,
        )
        if not claims:
            raise InvalidVerificationTokenError("Invalid or expired Google login token")

        phone = claims["phone"]
        google_sub = claims["google_sub"]
        email = claims.get("email", "")
        user_id = UUID(claims["user_id"])

        verification = await self.verification_repo.find_valid(phone)
        if not verification:
            raise OTPExpiredError("OTP expired or not found")

        if verification.attempt_count >= verification.max_attempts:
            raise OTPMaxAttemptsError("Too many failed attempts. Request a new OTP.")

        incoming_hash = hashlib.sha256(otp_code.encode()).hexdigest()
        if verification.code_hash != incoming_hash:
            await self.verification_repo.increment_attempts(verification.id)
            raise OTPInvalidError("Invalid OTP code")

        user = await self.user_repo.find_by_id(user_id)
        if not user or user.phone != phone:
            raise InvalidSessionError("Existing phone user not found")

        existing_account = await self.account_repo.find_by_provider(
            "google", google_sub
        )
        if existing_account and existing_account.user_id != user.id:
            raise GoogleTokenError("Google account already belongs to another user")

        await self.verification_repo.mark_verified(verification.id)

        if email and user.email != email:
            email_owner = await self.user_repo.find_by_email(email)
            if email_owner and email_owner.id != user.id:
                raise GoogleTokenError("Google email already belongs to another user")
            user.email = email
            user = await self.user_repo.update(user)

        if not existing_account:
            await self.account_repo.save(
                Account(
                    id=uuid4(),
                    user_id=user.id,
                    provider="google",
                    provider_account_id=google_sub,
                )
            )

        session_id = uuid4()
        session, tokens = _build_session_and_tokens(
            user, session_id, self.settings, metadata
        )
        await self.session_repo.save(session)
        tokens["phone_required"] = False

        return tokens


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
            transferred_account_ids = []
            for account in google_accounts:
                await self.account_repo.transfer_to_user(
                    account.id, phone_owner.id
                )
                transferred_account_ids.append(str(account.id))

            remaining_accounts = await self.account_repo.find_by_user_id(
                current_user.id
            )
            if remaining_accounts:
                raise InvalidSessionError(
                    "Google account transfer failed during phone merge"
                )

            # Copy Google info to phone_owner if missing
            if not phone_owner.full_name and current_user.full_name:
                phone_owner.full_name = current_user.full_name
            google_email = current_user.email
            if google_email:
                current_user.email = None
                await self.user_repo.update(current_user)

            # Revoke all sessions for the temporary Google user
            await self.session_repo.revoke_all_for_user(current_user.id)

            # Delete the temporary Google user (cascade deletes sessions)
            await self.user_repo.delete(current_user.id)

            if google_email:
                phone_owner.email = google_email
            await self.user_repo.update(phone_owner)

            # The merged user is the phone_owner
            merged_user = phone_owner
            logger.info(
                "Google phone-link account merge completed",
                extra={
                    "temp_google_user_id": str(current_user.id),
                    "phone_owner_id": str(phone_owner.id),
                    "phone": phone,
                    "transferred_account_ids": transferred_account_ids,
                    "merged_user_id": str(merged_user.id),
                },
            )
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
