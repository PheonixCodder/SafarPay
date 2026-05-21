import logging

import pytest

from auth.infrastructure.messaging.console import ConsoleOTPProvider


@pytest.mark.asyncio
async def test_console_otp_provider_logs_masked_phone_and_code(caplog):
    provider = ConsoleOTPProvider()

    with caplog.at_level(logging.WARNING, logger="auth.messaging.console"):
        await provider.send_otp("+923001234567", "123456")

    assert "DEV OTP" in caplog.text
    assert "123456" in caplog.text
    assert "4567" in caplog.text
    assert "+92300123" not in caplog.text
