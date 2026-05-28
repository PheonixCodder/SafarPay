from __future__ import annotations

import json
import logging
from base64 import b64decode
from pathlib import Path
from typing import Any

import anyio
import httpx

from ..domain.models import Notification

logger = logging.getLogger("notification.push")

FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
FCM_V1_URL_TEMPLATE = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"


class PushClient:
    def __init__(
        self,
        *,
        server_key: str = "",
        send_url: str = "",
        service_account_json: str = "",
        service_account_json_base64: str = "",
        service_account_file: str = "",
        project_id: str = "",
        credentials: Any | None = None,
    ) -> None:
        self._server_key = server_key
        self._send_url = send_url or "https://fcm.googleapis.com/fcm/send"
        self._project_id = project_id
        self._last_error_code = ""
        self._credentials = credentials or self._load_credentials(
            service_account_json=service_account_json,
            service_account_json_base64=service_account_json_base64,
            service_account_file=service_account_file,
        )
        if self._credentials is not None and not self._project_id:
            self._project_id = getattr(self._credentials, "project_id", "") or ""

    async def send_to_token(self, token: str, notification: Notification) -> bool:
        self._last_error_code = ""
        if self._credentials is not None:
            return await self._send_v1(token, notification)

        if not self._server_key:
            logger.info("FCM credentials not configured. Skipping push notification.")
            return False

        payload: dict[str, Any] = {
            "to": token,
            "priority": "high",
            "notification": {
                "title": notification.title,
                "body": notification.message,
            },
            "data": {
                "notification_id": str(notification.id),
                "type": notification.type.value,
                "title": notification.title,
                "body": notification.message,
                "deeplink": notification.deeplink or "",
                **{key: str(value) for key, value in notification.metadata.items() if value is not None},
            },
        }
        if _is_actionable_notification(notification):
            payload.pop("notification", None)
        if _is_driver_ride_request(notification):
            ride_id = str(notification.metadata.get("ride_id") or notification.source_event_id or "")
            payload["time_to_live"] = 45
            payload["collapse_key"] = f"driver_ride_request:{ride_id}"
            payload["android_channel_id"] = "ride_alerts"
        if _is_communication_call(notification):
            call_id = str(notification.metadata.get("call_id") or notification.source_event_id or "")
            payload["time_to_live"] = 30
            payload["collapse_key"] = f"communication_call:{call_id}"
            payload["android_channel_id"] = "ride_calls"
        headers = {
            "Authorization": f"key={self._server_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(self._send_url, json=payload, headers=headers)
            if 200 <= response.status_code < 300:
                return True
            self._last_error_code = _fcm_error_code(response.text)
            logger.warning("FCM push failed status=%s body=%s", response.status_code, response.text[:300])
        except Exception:
            logger.exception("FCM push request failed")
        return False

    def _load_credentials(
        self,
        *,
        service_account_json: str,
        service_account_json_base64: str,
        service_account_file: str,
    ) -> Any | None:
        if not service_account_json and not service_account_json_base64 and not service_account_file:
            return None

        try:
            from google.oauth2 import service_account
        except ImportError:
            logger.exception("google-auth is required for FCM service account credentials")
            return None

        if service_account_json:
            try:
                info = json.loads(service_account_json)
            except json.JSONDecodeError:
                logger.exception("FCM service account JSON is not valid JSON")
                return None
            return service_account.Credentials.from_service_account_info(
                info,
                scopes=[FCM_SCOPE],
            )

        if service_account_json_base64:
            try:
                info = json.loads(b64decode(service_account_json_base64).decode("utf-8"))
            except (ValueError, json.JSONDecodeError):
                logger.exception("FCM base64 service account JSON is not valid")
                return None
            return service_account.Credentials.from_service_account_info(
                info,
                scopes=[FCM_SCOPE],
            )

        if service_account_file:
            path = Path(service_account_file)
            if not path.exists():
                logger.warning("FCM service account file does not exist: %s", path)
                return None
            return service_account.Credentials.from_service_account_file(
                str(path),
                scopes=[FCM_SCOPE],
            )

        return None

    async def _send_v1(self, token: str, notification: Notification) -> bool:
        if not self._project_id:
            logger.warning("FCM project id not configured. Skipping push notification.")
            return False

        access_token = await self._access_token()
        if not access_token:
            return False

        payload: dict[str, Any] = {
            "message": {
                "token": token,
                "notification": {
                    "title": notification.title,
                    "body": notification.message,
                },
                "data": {
                    "notification_id": str(notification.id),
                    "type": notification.type.value,
                    "title": notification.title,
                    "body": notification.message,
                    "deeplink": notification.deeplink or "",
                    **{
                        key: str(value)
                        for key, value in notification.metadata.items()
                        if value is not None
                    },
                },
                "android": {
                    "priority": "HIGH",
                },
                "apns": {
                    "headers": {
                        "apns-priority": "10",
                    },
                },
            }
        }
        if _is_actionable_notification(notification):
            payload["message"].pop("notification", None)
        if _is_driver_ride_request(notification):
            ride_id = str(notification.metadata.get("ride_id") or notification.source_event_id or "")
            payload["message"]["android"] |= {
                "ttl": "45s",
                "collapse_key": f"driver_ride_request:{ride_id}",
            }
        if _is_communication_call(notification):
            call_id = str(notification.metadata.get("call_id") or notification.source_event_id or "")
            payload["message"]["android"] |= {
                "ttl": "30s",
                "collapse_key": f"communication_call:{call_id}",
            }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(
                    FCM_V1_URL_TEMPLATE.format(project_id=self._project_id),
                    json=payload,
                    headers=headers,
                )
            if 200 <= response.status_code < 300:
                return True
            self._last_error_code = _fcm_error_code(response.text)
            logger.warning("FCM v1 push failed status=%s body=%s", response.status_code, response.text[:300])
        except Exception:
            logger.exception("FCM v1 push request failed")
        return False

    async def _access_token(self) -> str:
        credentials = self._credentials
        if credentials is None:
            return ""
        try:
            if not getattr(credentials, "valid", False):
                from google.auth.transport.requests import Request

                await anyio.to_thread.run_sync(credentials.refresh, Request())
            return str(getattr(credentials, "token", "") or "")
        except Exception:
            logger.exception("Unable to refresh FCM service account credentials")
            return ""

    @property
    def last_error_code(self) -> str:
        return self._last_error_code


class NullPushClient(PushClient):
    def __init__(self) -> None:
        super().__init__(server_key="")


def _is_driver_ride_request(notification: Notification) -> bool:
    return notification.metadata.get("notification_kind") == "driver_ride_request"


def _is_communication_call(notification: Notification) -> bool:
    return notification.metadata.get("notification_kind") == "communication_call" or bool(
        notification.metadata.get("present_as_call")
    )


def _is_communication_message(notification: Notification) -> bool:
    return notification.metadata.get("notification_kind") == "communication_message"


def _is_actionable_notification(notification: Notification) -> bool:
    return _is_driver_ride_request(notification)


def _fcm_error_code(response_text: str) -> str:
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return ""
    details = data.get("error", {}).get("details", [])
    if isinstance(details, list):
        for item in details:
            if isinstance(item, dict) and item.get("errorCode"):
                return str(item["errorCode"])
    status = data.get("error", {}).get("status")
    return str(status or "")
