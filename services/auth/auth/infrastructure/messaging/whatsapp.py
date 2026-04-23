"""WhatsApp OTP provider via pywa authentication template.

Uses pywa's send_template() with an AUTHENTICATION category template
and COPY_CODE OTP button, as required by Meta's Business API policy.
"""
from __future__ import annotations

import asyncio
import inspect
import logging

from pywa import WhatsApp
from pywa.types import Template as WaTemplate

from auth.domain.interfaces import OTPProviderProtocol

logger = logging.getLogger("auth.messaging.whatsapp")


class PywaOTPProvider(OTPProviderProtocol):
    def __init__(self, token: str, phone_id: str, template_name: str) -> None:
        self.client = WhatsApp(token=token, phone_id=phone_id)
        self.template_name = template_name

    async def send_otp(self, phone: str, code: str) -> None:
        """Send OTP via WhatsApp authentication template with COPY_CODE button."""
        template = WaTemplate(
            name=self.template_name,
            language=WaTemplate.Language.ENGLISH_US,
            body=WaTemplate.Body(code=code),
            buttons=WaTemplate.OTPButton(
                otp_type=WaTemplate.OTPButton.OtpType.COPY_CODE,
            ),
        )

        send_fn = self.client.send_template

        if inspect.iscoroutinefunction(send_fn):
            await send_fn(to=phone, template=template)
        else:
            await asyncio.to_thread(send_fn, to=phone, template=template)

        logger.info("OTP template sent", extra={"phone": phone[-4:]})