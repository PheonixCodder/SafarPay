from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from auth.application.use_cases import (
    GoogleVerifyTokenUseCase,
    LinkPhoneUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    SendOTPUseCase,
    VerifyOTPUseCase,
)
from auth.domain.exceptions import (
    GoogleTokenError,
    InvalidSessionError,
    InvalidVerificationTokenError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    UserAlreadyExistsError,
)
from auth.domain.models import Account, Session, User, UserRole, Verification
from sp.core.config import Settings
from sp.infrastructure.security.jwt import create_verification_token, verify_token


def settings() -> Settings:
    return Settings(JWT_SECRET="test-secret-for-auth-suite-32-bytes", JWT_ALGORITHM="HS256")


class FakeOTPProvider:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_otp(self, phone: str, code: str) -> None:
        self.sent.append((phone, code))


class FakeVerificationRepo:
    def __init__(self) -> None:
        self.items: dict[UUID, Verification] = {}
        self.valid: Verification | None = None
        self.verified_ids: list[UUID] = []

    async def create(self, verification: Verification) -> Verification:
        self.items[verification.id] = verification
        self.valid = verification
        return verification

    async def find_valid(self, identifier: str) -> Verification | None:
        if self.valid and self.valid.identifier == identifier:
            return self.valid
        return None

    async def mark_verified(self, verification_id: UUID) -> None:
        self.verified_ids.append(verification_id)
        if verification_id in self.items:
            self.items[verification_id].verified_at = datetime.now(timezone.utc)

    async def increment_attempts(self, verification_id: UUID) -> int:
        if self.valid and self.valid.id == verification_id:
            self.valid.attempt_count += 1
            return self.valid.attempt_count
        return 0


class FakeUserRepo:
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}
        self.deleted: list[UUID] = []

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def find_by_phone(self, phone: str) -> User | None:
        return next((u for u in self.users.values() if u.phone == phone), None)

    async def find_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def save(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def delete(self, user_id: UUID) -> bool:
        self.deleted.append(user_id)
        self.users.pop(user_id, None)
        return True


class FakeSessionRepo:
    def __init__(self) -> None:
        self.sessions: dict[UUID, Session] = {}
        self.revoked_user_ids: list[UUID] = []

    async def find_by_id(self, session_id: UUID) -> Session | None:
        return self.sessions.get(session_id)

    async def find_by_hash(self, token_hash: str) -> Session | None:
        return next((s for s in self.sessions.values() if s.refresh_token_hash == token_hash), None)

    async def find_active_by_user(self, user_id: UUID) -> list[Session]:
        return [s for s in self.sessions.values() if s.user_id == user_id and not s.is_revoked]

    async def save(self, session: Session) -> Session:
        self.sessions[session.id] = session
        return session

    async def update(self, session: Session) -> Session:
        self.sessions[session.id] = session
        return session

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        self.revoked_user_ids.append(user_id)
        for session in self.sessions.values():
            if session.user_id == user_id:
                session.is_revoked = True


class FakeAccountRepo:
    def __init__(self) -> None:
        self.accounts: dict[UUID, Account] = {}
        self.transfers: list[tuple[UUID, UUID]] = []

    async def find_by_provider(self, provider: str, provider_account_id: str) -> Account | None:
        return next(
            (
                a
                for a in self.accounts.values()
                if a.provider == provider and a.provider_account_id == provider_account_id
            ),
            None,
        )

    async def find_by_user_id(self, user_id: UUID) -> list[Account]:
        return [a for a in self.accounts.values() if a.user_id == user_id]

    async def save(self, account: Account) -> Account:
        self.accounts[account.id] = account
        return account

    async def transfer_to_user(self, account_id: UUID, new_user_id: UUID) -> None:
        self.transfers.append((account_id, new_user_id))
        self.accounts[account_id].user_id = new_user_id


class FakeGoogleVerifier:
    def __init__(self, claims: dict | None = None, error: Exception | None = None) -> None:
        self.claims = claims or {
            "sub": "google-1",
            "email": "g@example.com",
            "name": "Google User",
            "picture": "https://img",
        }
        self.error = error

    async def verify(self, id_token: str) -> dict:
        if self.error:
            raise self.error
        return self.claims


@pytest.mark.asyncio
async def test_send_otp_hashes_code_and_sends_provider_message() -> None:
    otp_provider = FakeOTPProvider()
    verification_repo = FakeVerificationRepo()
    await SendOTPUseCase(otp_provider, verification_repo).execute("+923001234567")

    verification = next(iter(verification_repo.items.values()))
    sent_phone, sent_code = otp_provider.sent[0]

    assert sent_phone == "+923001234567"
    assert sent_code not in verification.code_hash
    assert hashlib.sha256(sent_code.encode()).hexdigest() == verification.code_hash


@pytest.mark.asyncio
async def test_verify_otp_success_marks_verified_and_returns_phone_token() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    code = "123456"
    verification = Verification(
        id=uuid4(),
        identifier="+923001234567",
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    verification_repo.valid = verification
    verification_repo.items[verification.id] = verification

    token = await VerifyOTPUseCase(verification_repo, s).execute(verification.identifier, code)

    assert verification_repo.verified_ids == [verification.id]
    assert token


@pytest.mark.asyncio
async def test_verify_otp_failure_paths_increment_and_block_attempts() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()

    with pytest.raises(OTPExpiredError):
        await VerifyOTPUseCase(verification_repo, s).execute("+923001234567", "123456")

    verification_repo.valid = Verification(
        id=uuid4(),
        identifier="+923001234567",
        code_hash=hashlib.sha256(b"123456").hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    with pytest.raises(OTPInvalidError):
        await VerifyOTPUseCase(verification_repo, s).execute("+923001234567", "000000")
    assert verification_repo.valid.attempt_count == 1

    verification_repo.valid.attempt_count = verification_repo.valid.max_attempts
    with pytest.raises(OTPMaxAttemptsError):
        await VerifyOTPUseCase(verification_repo, s).execute("+923001234567", "123456")


@pytest.mark.asyncio
async def test_register_creates_verified_passenger_session_and_tokens() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    token = create_verification_token("+923001234567", s.JWT_SECRET, s.JWT_ALGORITHM)

    tokens = await RegisterUseCase(user_repo, session_repo, s).execute(
        token,
        "Passenger One",
        {"user_agent": "pytest", "ip_address": "127.0.0.1"},
    )

    user = next(iter(user_repo.users.values()))
    session = next(iter(session_repo.sessions.values()))
    payload = verify_token(tokens["access_token"], s.JWT_SECRET, s.JWT_ALGORITHM)

    assert user.phone == "+923001234567"
    assert user.role == UserRole.PASSENGER
    assert user.is_verified
    assert session.user_id == user.id
    assert session.refresh_token_hash == hashlib.sha256(tokens["refresh_token"].encode()).hexdigest()
    assert payload and payload.user_id == user.id


@pytest.mark.asyncio
async def test_register_rejects_invalid_token_and_duplicate_phone() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    uc = RegisterUseCase(user_repo, session_repo, s)

    with pytest.raises(InvalidVerificationTokenError):
        await uc.execute("bad-token", "Passenger One", {})

    user = User.create(UserRole.PASSENGER, phone="+923001234567", is_verified=True)
    await user_repo.save(user)
    token = create_verification_token(user.phone or "", s.JWT_SECRET, s.JWT_ALGORITHM)
    with pytest.raises(UserAlreadyExistsError):
        await uc.execute(token, "Passenger One", {})


@pytest.mark.asyncio
async def test_google_verify_creates_new_user_or_returns_existing_linked_user() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    uc = GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        s,
    )

    new_tokens = await uc.execute("token", {})
    new_user = next(iter(user_repo.users.values()))

    assert new_tokens["phone_required"] is True
    assert new_user.email == "g@example.com"
    assert len(account_repo.accounts) == 1

    new_user.is_verified = True
    existing_tokens = await uc.execute("token", {})
    assert existing_tokens["phone_required"] is False
    assert len(user_repo.users) == 1


@pytest.mark.asyncio
async def test_google_verify_wraps_verifier_errors() -> None:
    with pytest.raises(GoogleTokenError):
        await GoogleVerifyTokenUseCase(
            FakeGoogleVerifier(error=ValueError("bad")),
            FakeUserRepo(),
            FakeAccountRepo(),
            FakeSessionRepo(),
            settings(),
        ).execute("bad", {})


@pytest.mark.asyncio
async def test_link_phone_simple_link_and_conflict_merge() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()

    google_user = await user_repo.save(User.create(UserRole.PASSENGER, email="g@example.com"))
    token = create_verification_token("+923001234567", s.JWT_SECRET, s.JWT_ALGORITHM)
    tokens = await LinkPhoneUseCase(user_repo, account_repo, session_repo, s).execute(
        google_user.id, token, {}
    )
    assert tokens["phone_required"] is False
    assert user_repo.users[google_user.id].phone == "+923001234567"
    assert user_repo.users[google_user.id].is_verified

    temp_google_user = await user_repo.save(
        User.create(UserRole.PASSENGER, full_name="Google Name", email="new@example.com")
    )
    phone_owner = await user_repo.save(
        User.create(UserRole.PASSENGER, phone="+923009999999", is_verified=True)
    )
    account = await account_repo.save(
        Account(id=uuid4(), user_id=temp_google_user.id, provider="google", provider_account_id="g2")
    )
    merge_token = create_verification_token(phone_owner.phone or "", s.JWT_SECRET, s.JWT_ALGORITHM)

    await LinkPhoneUseCase(user_repo, account_repo, session_repo, s).execute(
        temp_google_user.id, merge_token, {}
    )

    assert account_repo.accounts[account.id].user_id == phone_owner.id
    assert account_repo.transfers == [(account.id, phone_owner.id)]
    assert temp_google_user.id in user_repo.deleted
    assert session_repo.revoked_user_ids == [temp_google_user.id]
    assert user_repo.users[phone_owner.id].email == "new@example.com"


@pytest.mark.asyncio
async def test_refresh_token_rotates_hash_and_rejects_invalid_sessions() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    user = await user_repo.save(User.create(UserRole.PASSENGER, email="p@example.com"))
    old_refresh = "old-refresh"
    session = await session_repo.save(
        Session(
            id=uuid4(),
            user_id=user.id,
            refresh_token_hash=hashlib.sha256(old_refresh.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
    )

    tokens = await RefreshTokenUseCase(session_repo, user_repo, s).execute(old_refresh)

    assert session.refresh_token_hash == hashlib.sha256(tokens["refresh_token"].encode()).hexdigest()
    assert session.refresh_token_hash != hashlib.sha256(old_refresh.encode()).hexdigest()

    session.is_revoked = True
    with pytest.raises(InvalidSessionError):
        await RefreshTokenUseCase(session_repo, user_repo, s).execute(tokens["refresh_token"])
