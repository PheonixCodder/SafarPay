"""Verification rejection resolver service."""
from uuid import UUID

from ...domain.interfaces import VerificationRejectionRepositoryProtocol


class RejectionResolver:
    """Helper service to encapsulate rejection fetching and resolving logic."""
    
    def __init__(self, rejection_repo: VerificationRejectionRepositoryProtocol) -> None:
        self._rejection_repo = rejection_repo

    async def get_rejection_reason(self, document_id: UUID) -> str | None:
        """Fetch the latest active rejection reason for a document."""
        rejection = await self._rejection_repo.find_active_rejection_by_document(document_id)
        if not rejection:
            return None
        return rejection.admin_comment or rejection.rejection_reason_code

    async def resolve_previous_rejections(self, document_id: UUID) -> None:
        """Mark all active rejections for a document as resolved."""
        await self._rejection_repo.mark_rejections_resolved(document_id)
