from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from auth.application.use_cases import (
    GoogleVerifyTokenUseCase,
    LinkPhoneUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    SendOTPUseCase,
    UpdateUserProfileUseCase,
    VerifyOTPUseCase,
    VerifyGoogleExistingPhoneUseCase,
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
    return Settings()


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
async def test_verify_otp_new_phone_returns_complete_profile_registration_token() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    code = "123456"
    verification = Verification(
        id=uuid4(),
        identifier="+923001234567",
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    verification_repo.valid = verification
    verification_repo.items[verification.id] = verification

    result = await VerifyOTPUseCase(
        verification_repo,
        user_repo,
        session_repo,
        s,
    ).execute(verification.identifier, code, {})

    assert verification_repo.verified_ids == [verification.id]
    assert result["next_step"] == "complete_profile"
    assert result["registration_token"]
    assert "access_token" not in result


@pytest.mark.asyncio
async def test_verify_otp_existing_phone_returns_login_tokens() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Passenger",
            phone="+923001234567",
            is_verified=True,
        )
    )
    code = "123456"
    verification = Verification(
        id=uuid4(),
        identifier=user.phone or "",
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    verification_repo.valid = verification
    verification_repo.items[verification.id] = verification

    result = await VerifyOTPUseCase(
        verification_repo,
        user_repo,
        session_repo,
        s,
    ).execute(verification.identifier, code, {"user_agent": "pytest"})

    session = next(iter(session_repo.sessions.values()))
    payload = verify_token(result["access_token"], s.JWT_SECRET, s.JWT_ALGORITHM)

    assert result["next_step"] == "login"
    assert result["refresh_token"]
    assert result["phone_required"] is False
    assert session.user_id == user.id
    assert payload and payload.user_id == user.id


@pytest.mark.asyncio
async def test_verify_otp_phone_link_returns_registration_token_even_for_existing_phone() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    user = await user_repo.save(
        User.create(UserRole.PASSENGER, phone="+923001234567", is_verified=True)
    )
    code = "123456"
    verification = Verification(
        id=uuid4(),
        identifier=user.phone or "",
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    verification_repo.valid = verification
    verification_repo.items[verification.id] = verification

    result = await VerifyOTPUseCase(
        verification_repo,
        user_repo,
        session_repo,
        s,
    ).execute(verification.identifier, code, {}, purpose="phone_link")

    assert result["next_step"] == "link_phone"
    assert result["registration_token"]
    assert "access_token" not in result


@pytest.mark.asyncio
async def test_verify_otp_failure_paths_increment_and_block_attempts() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    use_case = VerifyOTPUseCase(verification_repo, user_repo, session_repo, s)

    with pytest.raises(OTPExpiredError):
        await use_case.execute("+923001234567", "123456", {})

    verification_repo.valid = Verification(
        id=uuid4(),
        identifier="+923001234567",
        code_hash=hashlib.sha256(b"123456").hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    with pytest.raises(OTPInvalidError):
        await use_case.execute("+923001234567", "000000", {})
    assert verification_repo.valid.attempt_count == 1

    verification_repo.valid.attempt_count = verification_repo.valid.max_attempts
    with pytest.raises(OTPMaxAttemptsError):
        await use_case.execute("+923001234567", "123456", {})


@pytest.mark.asyncio
async def test_register_creates_verified_passenger_session_and_tokens() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    token = create_verification_token("+923001234567", s.JWT_SECRET, s.JWT_ALGORITHM)

    tokens = await RegisterUseCase(user_repo, session_repo, s).execute(
        token,
        "Passenger One",
        "passenger@example.com",
        "male",
        date(1998, 5, 17),
        {"user_agent": "pytest", "ip_address": "127.0.0.1"},
    )

    user = next(iter(user_repo.users.values()))
    session = next(iter(session_repo.sessions.values()))
    payload = verify_token(tokens["access_token"], s.JWT_SECRET, s.JWT_ALGORITHM)

    assert user.phone == "+923001234567"
    assert user.email == "passenger@example.com"
    assert user.gender == "male"
    assert user.date_of_birth == date(1998, 5, 17)
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
        await uc.execute(
            "bad-token",
            "Passenger One",
            "passenger@example.com",
            "male",
            date(1998, 5, 17),
            {},
        )

    user = User.create(UserRole.PASSENGER, phone="+923001234567", is_verified=True)
    await user_repo.save(user)
    token = create_verification_token(user.phone or "", s.JWT_SECRET, s.JWT_ALGORITHM)
    with pytest.raises(UserAlreadyExistsError):
        await uc.execute(
            token,
            "Passenger One",
            "passenger@example.com",
            "male",
            date(1998, 5, 17),
            {},
        )


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    session_repo = FakeSessionRepo()
    await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Existing",
            email="passenger@example.com",
            phone="+923001111111",
            is_verified=True,
        )
    )
    token = create_verification_token("+923009999999", s.JWT_SECRET, s.JWT_ALGORITHM)

    with pytest.raises(UserAlreadyExistsError):
        await RegisterUseCase(user_repo, session_repo, s).execute(
            token,
            "Passenger One",
            "passenger@example.com",
            "male",
            date(1998, 5, 17),
            {},
        )


@pytest.mark.asyncio
async def test_update_user_profile_updates_editable_fields_and_rejects_email_conflict() -> None:
    user_repo = FakeUserRepo()
    user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Old Name",
            email="old@example.com",
            phone="+923001234567",
            is_verified=True,
        )
    )
    await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Other",
            email="other@example.com",
            phone="+923001111111",
            is_verified=True,
        )
    )

    updated = await UpdateUserProfileUseCase(user_repo).execute(
        user.id,
        full_name="New Name",
        email="new@example.com",
        gender="female",
        date_of_birth=date(1997, 7, 9),
    )

    assert updated.full_name == "New Name"
    assert updated.email == "new@example.com"
    assert updated.gender == "female"
    assert updated.date_of_birth == date(1997, 7, 9)
    assert updated.phone == "+923001234567"

    with pytest.raises(UserAlreadyExistsError):
        await UpdateUserProfileUseCase(user_repo).execute(
            user.id,
            email="other@example.com",
        )


@pytest.mark.asyncio
async def test_google_verify_creates_new_user_or_returns_existing_linked_user() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    otp_provider = FakeOTPProvider()
    verification_repo = FakeVerificationRepo()
    uc = GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        otp_provider,
        verification_repo,
        s,
    )

    new_tokens = await uc.execute("token", {})
    new_user = next(iter(user_repo.users.values()))

    assert new_tokens["phone_required"] is True
    assert new_user.email == "g@example.com"
    assert len(account_repo.accounts) == 1

    new_user.is_verified = True
    new_user.email = "old-google@example.com"
    existing_tokens = await uc.execute("token", {})
    assert existing_tokens["phone_required"] is False
    assert user_repo.users[new_user.id].email == "g@example.com"
    assert len(user_repo.users) == 1
    assert otp_provider.sent == []
    assert verification_repo.valid is None


@pytest.mark.asyncio
async def test_google_verify_existing_linked_user_with_phone_requires_otp_before_tokens() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    otp_provider = FakeOTPProvider()
    verification_repo = FakeVerificationRepo()
    linked_user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Existing User",
            email="old-google@example.com",
            phone="+923219898782",
            is_verified=True,
        )
    )
    await account_repo.save(
        Account(
            id=uuid4(),
            user_id=linked_user.id,
            provider="google",
            provider_account_id="google-1",
        )
    )

    result = await GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        otp_provider,
        verification_repo,
        s,
    ).execute("token", {"user_agent": "pytest"})

    assert result["next_step"] == "verify_existing_phone"
    assert result["masked_phone"] == "******8782"
    assert result["google_login_token"]
    assert result["phone_required"] is False
    assert "access_token" not in result
    assert user_repo.users[linked_user.id].email == "g@example.com"
    assert otp_provider.sent[0][0] == linked_user.phone
    assert verification_repo.valid and verification_repo.valid.identifier == linked_user.phone
    assert len(session_repo.sessions) == 0


@pytest.mark.asyncio
async def test_google_verify_wraps_verifier_errors() -> None:
    with pytest.raises(GoogleTokenError):
        await GoogleVerifyTokenUseCase(
            FakeGoogleVerifier(error=ValueError("bad")),
            FakeUserRepo(),
            FakeAccountRepo(),
            FakeSessionRepo(),
            FakeOTPProvider(),
            FakeVerificationRepo(),
            settings(),
        ).execute("bad", {})


@pytest.mark.asyncio
async def test_google_verify_existing_email_with_phone_sends_otp_and_returns_masked_step() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    otp_provider = FakeOTPProvider()
    verification_repo = FakeVerificationRepo()
    existing_user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Existing User",
            email="g@example.com",
            phone="+923219898782",
            is_verified=True,
        )
    )

    result = await GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        otp_provider,
        verification_repo,
        s,
    ).execute("token", {})

    assert result["next_step"] == "verify_existing_phone"
    assert result["masked_phone"] == "******8782"
    assert result["google_login_token"]
    assert result["phone_required"] is False
    assert "access_token" not in result
    assert otp_provider.sent[0][0] == existing_user.phone
    assert verification_repo.valid and verification_repo.valid.identifier == existing_user.phone
    assert len(account_repo.accounts) == 0
    assert len(session_repo.sessions) == 0


@pytest.mark.asyncio
async def test_google_verify_existing_email_without_phone_links_user_and_requires_phone() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    existing_user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Existing User",
            email="g@example.com",
            is_verified=False,
        )
    )

    result = await GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        FakeOTPProvider(),
        FakeVerificationRepo(),
        s,
    ).execute("token", {})

    account = next(iter(account_repo.accounts.values()))
    session = next(iter(session_repo.sessions.values()))
    assert result["phone_required"] is True
    assert account.user_id == existing_user.id
    assert account.provider == "google"
    assert account.provider_account_id == "google-1"
    assert session.user_id == existing_user.id
    assert len(user_repo.users) == 1


@pytest.mark.asyncio
async def test_verify_google_existing_phone_links_account_and_returns_tokens() -> None:
    s = settings()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    verification_repo = FakeVerificationRepo()
    existing_user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            full_name="Existing User",
            email="g@example.com",
            phone="+923219898782",
            is_verified=True,
        )
    )
    code = "123456"
    verification = Verification(
        id=uuid4(),
        identifier=existing_user.phone or "",
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    verification_repo.valid = verification
    verification_repo.items[verification.id] = verification
    google_step = await GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        FakeOTPProvider(),
        FakeVerificationRepo(),
        s,
    ).execute("token", {})

    result = await VerifyGoogleExistingPhoneUseCase(
        verification_repo,
        user_repo,
        account_repo,
        session_repo,
        s,
    ).execute(
        google_step["google_login_token"],
        code,
        {"user_agent": "pytest"},
    )

    account = next(iter(account_repo.accounts.values()))
    session = next(iter(session_repo.sessions.values()))
    payload = verify_token(result["access_token"], s.JWT_SECRET, s.JWT_ALGORITHM)
    assert verification_repo.verified_ids == [verification.id]
    assert result["phone_required"] is False
    assert account.user_id == existing_user.id
    assert account.provider == "google"
    assert account.provider_account_id == "google-1"
    assert session.user_id == existing_user.id
    assert payload and payload.user_id == existing_user.id


@pytest.mark.asyncio
async def test_verify_google_existing_phone_rejects_invalid_token_and_bad_otp() -> None:
    s = settings()
    verification_repo = FakeVerificationRepo()
    user_repo = FakeUserRepo()
    account_repo = FakeAccountRepo()
    session_repo = FakeSessionRepo()
    use_case = VerifyGoogleExistingPhoneUseCase(
        verification_repo,
        user_repo,
        account_repo,
        session_repo,
        s,
    )

    with pytest.raises(InvalidVerificationTokenError):
        await use_case.execute("bad-token", "123456", {})

    existing_user = await user_repo.save(
        User.create(
            UserRole.PASSENGER,
            email="g@example.com",
            phone="+923219898782",
            is_verified=True,
        )
    )
    step = await GoogleVerifyTokenUseCase(
        FakeGoogleVerifier(),
        user_repo,
        account_repo,
        session_repo,
        FakeOTPProvider(),
        FakeVerificationRepo(),
        s,
    ).execute("token", {})
    verification_repo.valid = Verification(
        id=uuid4(),
        identifier=existing_user.phone or "",
        code_hash=hashlib.sha256(b"123456").hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    with pytest.raises(OTPInvalidError):
        await use_case.execute(step["google_login_token"], "000000", {})
    assert verification_repo.valid.attempt_count == 1


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
        User.create(
            UserRole.PASSENGER,
            full_name="Phone Name",
            email="old-phone@example.com",
            phone="+923009999999",
            is_verified=True,
        )
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
    assert all(
        saved_account.user_id != temp_google_user.id
        for saved_account in account_repo.accounts.values()
    )
    assert user_repo.users[phone_owner.id].full_name == "Phone Name"
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
