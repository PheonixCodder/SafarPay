"""SQLAlchemy repositories for communication service."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import (
    CallStatus,
    Conversation,
    ConversationParticipant,
    ConversationStatus,
    MediaUploadStatus,
    Message,
    MessageMedia,
    ParticipantRole,
    VoiceCall,
)
from .orm_models import (
    CallSignalingEventORM,
    CommunicationEventORM,
    CommunicationEventType,
    ConversationORM,
    ConversationParticipantORM,
    MessageMediaORM,
    MessageORM,
    SignalType,
    VoiceCallORM,
)


def _conversation_to_domain(o: ConversationORM) -> Conversation:
    return Conversation(
        id=o.id,
        service_request_id=o.service_request_id,
        passenger_user_id=o.passenger_user_id,
        driver_id=o.driver_id,
        driver_user_id=o.driver_user_id,
        status=ConversationStatus(o.status.value),
        opened_at=o.opened_at,
        closed_at=o.closed_at,
        created_at=o.created_at,
        updated_at=o.updated_at,
    )


def _participant_to_domain(o: ConversationParticipantORM) -> ConversationParticipant:
    return ConversationParticipant(
        id=o.id,
        conversation_id=o.conversation_id,
        role=ParticipantRole(o.role.value),
        user_id=o.user_id,
        driver_id=o.driver_id,
        joined_at=o.joined_at,
    )


def _message_to_domain(o: MessageORM) -> Message:
    from ..domain.models import MessageStatus, MessageType
    return Message(
        id=o.id,
        conversation_id=o.conversation_id,
        sender_participant_id=o.sender_participant_id,
        message_type=MessageType(o.message_type.value),
        status=MessageStatus(o.status.value),
        body=o.body,
        reply_to_message_id=o.reply_to_message_id,
        sent_at=o.sent_at,
        delivered_at=o.delivered_at,
        read_at=o.read_at,
        deleted_at=o.deleted_at,
    )


def _media_to_domain(o: MessageMediaORM) -> MessageMedia:
    from ..domain.models import MediaType
    return MessageMedia(
        id=o.id,
        message_id=o.message_id,
        conversation_id=o.conversation_id,
        uploader_participant_id=o.uploader_participant_id,
        media_type=MediaType(o.media_type.value),
        file_key=o.file_key,
        mime_type=o.mime_type,
        file_name=o.file_name,
        file_size_bytes=o.file_size_bytes,
        duration_seconds=float(o.duration_seconds) if o.duration_seconds is not None else None,
        checksum_sha256=o.checksum_sha256,
        upload_status=MediaUploadStatus(o.upload_status.value),
        created_at=o.created_at,
    )


def _call_to_domain(o: VoiceCallORM) -> VoiceCall:
    return VoiceCall(
        id=o.id,
        conversation_id=o.conversation_id,
        caller_participant_id=o.caller_participant_id,
        callee_participant_id=o.callee_participant_id,
        status=CallStatus(o.status.value),
        started_at=o.started_at,
        accepted_at=o.accepted_at,
        ended_at=o.ended_at,
        end_reason=o.end_reason,
    )


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm = result.scalar_one_or_none()
        return _conversation_to_domain(orm) if orm else None

    async def find_by_ride(self, service_request_id: UUID) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationORM).where(ConversationORM.service_request_id == service_request_id)
        )
        orm = result.scalar_one_or_none()
        return _conversation_to_domain(orm) if orm else None

    async def find_for_actor(
        self,
        user_id: UUID,
        driver_id: UUID | None,
        status_filter: ConversationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        conditions = [ConversationORM.passenger_user_id == user_id, ConversationORM.driver_user_id == user_id]
        if driver_id:
            conditions.append(ConversationORM.driver_id == driver_id)
        stmt = (
            select(ConversationORM)
            .where(or_(*conditions))
            .order_by(ConversationORM.opened_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status_filter:
            from .orm_models import ConversationStatus as OrmStatus
            stmt = stmt.where(ConversationORM.status == OrmStatus(status_filter.value))
        result = await self._session.execute(stmt)
        return [_conversation_to_domain(o) for o in result.scalars().all()]

    async def create_with_participants(self, conversation: Conversation) -> Conversation:
        from .orm_models import ConversationStatus as OrmConversationStatus
        from .orm_models import ParticipantRole as OrmParticipantRole

        existing = await self.find_by_ride(conversation.service_request_id)
        if existing:
            return existing

        orm = ConversationORM(
            id=conversation.id,
            service_request_id=conversation.service_request_id,
            passenger_user_id=conversation.passenger_user_id,
            driver_id=conversation.driver_id,
            driver_user_id=conversation.driver_user_id,
            status=OrmConversationStatus(conversation.status.value),
            opened_at=conversation.opened_at,
            closed_at=conversation.closed_at,
        )
        self._session.add(orm)
        self._session.add(
            ConversationParticipantORM(
                id=ConversationParticipant.passenger(conversation.id, conversation.passenger_user_id).id,
                conversation_id=conversation.id,
                role=OrmParticipantRole.PASSENGER,
                user_id=conversation.passenger_user_id,
                driver_id=None,
            )
        )
        self._session.add(
            ConversationParticipantORM(
                id=ConversationParticipant.driver(conversation.id, conversation.driver_user_id, conversation.driver_id).id,
                conversation_id=conversation.id,
                role=OrmParticipantRole.DRIVER,
                user_id=conversation.driver_user_id,
                driver_id=conversation.driver_id,
            )
        )
        await self.save_outbox_event(
            CommunicationEventType.CONVERSATION_OPENED,
            conversation.id,
            {
                "conversation_id": str(conversation.id),
                "ride_id": str(conversation.service_request_id),
                "passenger_user_id": str(conversation.passenger_user_id),
                "driver_id": str(conversation.driver_id),
            },
        )
        await self._session.flush()
        return conversation

    async def close_by_ride(self, service_request_id: UUID) -> Conversation | None:
        from .orm_models import ConversationStatus as OrmConversationStatus

        conversation = await self.find_by_ride(service_request_id)
        if not conversation:
            return None
        conversation.close()
        await self._session.execute(
            update(ConversationORM)
            .where(ConversationORM.id == conversation.id)
            .values(status=OrmConversationStatus.CLOSED, closed_at=conversation.closed_at)
        )
        await self.save_outbox_event(
            CommunicationEventType.CONVERSATION_CLOSED,
            conversation.id,
            {"conversation_id": str(conversation.id), "ride_id": str(service_request_id)},
        )
        await self._session.flush()
        return conversation

    async def get_driver_user_id(self, driver_id: UUID) -> UUID | None:
        result = await self._session.execute(
            text("SELECT user_id FROM verification.drivers WHERE id = :driver_id LIMIT 1"),
            {"driver_id": driver_id},
        )
        row = result.fetchone()
        return row[0] if row else None

    async def save_outbox_event(
        self,
        event_type: CommunicationEventType,
        aggregate_id: UUID,
        payload: dict[str, Any],
    ) -> None:
        self._session.add(
            CommunicationEventORM(event_type=event_type, aggregate_id=aggregate_id, payload=payload)
        )


class ParticipantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_for_actor(
        self,
        conversation_id: UUID,
        user_id: UUID,
        driver_id: UUID | None,
    ) -> ConversationParticipant | None:
        stmt = select(ConversationParticipantORM).where(
            ConversationParticipantORM.conversation_id == conversation_id,
            ConversationParticipantORM.user_id == user_id,
        )
        if driver_id:
            stmt = stmt.where(
                or_(ConversationParticipantORM.driver_id == driver_id, ConversationParticipantORM.driver_id.is_(None))
            )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return _participant_to_domain(orm) if orm else None

    async def find_other_participant(
        self,
        conversation_id: UUID,
        participant_id: UUID,
    ) -> ConversationParticipant | None:
        result = await self._session.execute(
            select(ConversationParticipantORM)
            .where(
                ConversationParticipantORM.conversation_id == conversation_id,
                ConversationParticipantORM.id != participant_id,
            )
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return _participant_to_domain(orm) if orm else None


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, message: Message) -> Message:
        from .orm_models import MessageStatus as OrmStatus
        from .orm_models import MessageType as OrmType

        orm = MessageORM(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_participant_id=message.sender_participant_id,
            message_type=OrmType(message.message_type.value),
            status=OrmStatus(message.status.value),
            body=message.body,
            reply_to_message_id=message.reply_to_message_id,
            sent_at=message.sent_at,
        )
        self._session.add(orm)
        self._session.add(
            CommunicationEventORM(
                event_type=CommunicationEventType.MESSAGE_SENT,
                aggregate_id=message.id,
                payload={
                    "conversation_id": str(message.conversation_id),
                    "message_id": str(message.id),
                    "message_type": message.message_type.value,
                },
            )
        )
        await self._session.flush()
        return _message_to_domain(orm)

    async def find_by_id(self, message_id: UUID) -> Message | None:
        result = await self._session.execute(select(MessageORM).where(MessageORM.id == message_id))
        orm = result.scalar_one_or_none()
        return _message_to_domain(orm) if orm else None

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_message_id: UUID | None = None,
    ) -> list[Message]:
        stmt = (
            select(MessageORM)
            .where(MessageORM.conversation_id == conversation_id)
            .order_by(MessageORM.sent_at.desc())
            .limit(limit)
        )
        if before_message_id:
            before = await self.find_by_id(before_message_id)
            if before:
                stmt = stmt.where(MessageORM.sent_at < before.sent_at)
        result = await self._session.execute(stmt)
        return [_message_to_domain(o) for o in reversed(result.scalars().all())]


class MediaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, media: MessageMedia) -> MessageMedia:
        from .orm_models import MediaType as OrmMediaType
        from .orm_models import MediaUploadStatus as OrmUploadStatus

        orm = MessageMediaORM(
            id=media.id,
            message_id=media.message_id,
            conversation_id=media.conversation_id,
            uploader_participant_id=media.uploader_participant_id,
            media_type=OrmMediaType(media.media_type.value),
            file_key=media.file_key,
            file_name=media.file_name,
            mime_type=media.mime_type,
            file_size_bytes=media.file_size_bytes,
            duration_seconds=media.duration_seconds,
            checksum_sha256=media.checksum_sha256,
            upload_status=OrmUploadStatus(media.upload_status.value),
        )
        self._session.add(orm)
        await self._session.flush()
        return _media_to_domain(orm)

    async def find_by_id(self, media_id: UUID) -> MessageMedia | None:
        result = await self._session.execute(select(MessageMediaORM).where(MessageMediaORM.id == media_id))
        orm = result.scalar_one_or_none()
        return _media_to_domain(orm) if orm else None

    async def find_by_message(self, message_id: UUID) -> MessageMedia | None:
        result = await self._session.execute(select(MessageMediaORM).where(MessageMediaORM.message_id == message_id))
        orm = result.scalar_one_or_none()
        return _media_to_domain(orm) if orm else None

    async def attach_to_message(self, media_id: UUID, message_id: UUID) -> MessageMedia:
        from .orm_models import MediaUploadStatus as OrmUploadStatus

        await self._session.execute(
            update(MessageMediaORM)
            .where(MessageMediaORM.id == media_id)
            .values(message_id=message_id, upload_status=OrmUploadStatus.UPLOADED)
        )
        self._session.add(
            CommunicationEventORM(
                event_type=CommunicationEventType.MEDIA_MESSAGE_SENT,
                aggregate_id=message_id,
                payload={"message_id": str(message_id), "media_id": str(media_id)},
            )
        )
        await self._session.flush()
        media = await self.find_by_id(media_id)
        if media is None:
            raise ValueError("Media not found after attach.")
        return media


class CallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, call: VoiceCall) -> VoiceCall:
        from .orm_models import CallStatus as OrmCallStatus

        orm = VoiceCallORM(
            id=call.id,
            conversation_id=call.conversation_id,
            caller_participant_id=call.caller_participant_id,
            callee_participant_id=call.callee_participant_id,
            status=OrmCallStatus(call.status.value),
            started_at=call.started_at,
            accepted_at=call.accepted_at,
            ended_at=call.ended_at,
            end_reason=call.end_reason,
        )
        self._session.add(orm)
        self._session.add(
            CommunicationEventORM(
                event_type=CommunicationEventType.CALL_STARTED,
                aggregate_id=call.id,
                payload={
                    "conversation_id": str(call.conversation_id),
                    "call_id": str(call.id),
                    "status": call.status.value,
                },
            )
        )
        await self._session.flush()
        return _call_to_domain(orm)

    async def find_by_id(self, call_id: UUID) -> VoiceCall | None:
        result = await self._session.execute(select(VoiceCallORM).where(VoiceCallORM.id == call_id))
        orm = result.scalar_one_or_none()
        return _call_to_domain(orm) if orm else None

    async def update(self, call: VoiceCall) -> VoiceCall:
        from .orm_models import CallStatus as OrmCallStatus

        await self._session.execute(
            update(VoiceCallORM)
            .where(VoiceCallORM.id == call.id)
            .values(
                status=OrmCallStatus(call.status.value),
                accepted_at=call.accepted_at,
                ended_at=call.ended_at,
                end_reason=call.end_reason,
            )
        )
        self._session.add(
            CommunicationEventORM(
                event_type=CommunicationEventType.CALL_UPDATED,
                aggregate_id=call.id,
                payload={
                    "conversation_id": str(call.conversation_id),
                    "call_id": str(call.id),
                    "status": call.status.value,
                },
            )
        )
        await self._session.flush()
        return call

    async def save_signal(
        self,
        call_id: UUID,
        sender_participant_id: UUID,
        signal_type: str,
        payload: dict[str, Any],
    ) -> None:
        self._session.add(
            CallSignalingEventORM(
                call_id=call_id,
                sender_participant_id=sender_participant_id,
                signal_type=SignalType(signal_type),
                payload=payload,
            )
        )
        await self._session.flush()
