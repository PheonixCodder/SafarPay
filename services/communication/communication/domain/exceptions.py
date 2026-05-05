"""Communication domain exceptions."""


class CommunicationDomainError(Exception):
    """Base communication domain error."""


class ConversationNotFoundError(CommunicationDomainError):
    """Conversation does not exist."""


class ConversationClosedError(CommunicationDomainError):
    """Conversation is closed for new communication."""


class UnauthorisedConversationAccessError(CommunicationDomainError):
    """Caller is not a participant in the conversation."""


class MessageNotFoundError(CommunicationDomainError):
    """Message does not exist."""


class MediaUploadError(CommunicationDomainError):
    """Media upload request or registration is invalid."""


class CallNotFoundError(CommunicationDomainError):
    """Voice call does not exist."""


class InvalidCallTransitionError(CommunicationDomainError):
    """Voice call lifecycle transition is invalid."""
