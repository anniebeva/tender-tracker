from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Tender, TenderStatus, TenderStatusHistory

ALLOWED_STATUS_TRANSITIONS = {
    TenderStatus.DRAFT: {TenderStatus.ACTIVE},
    TenderStatus.ACTIVE: {TenderStatus.WON, TenderStatus.LOST},
    TenderStatus.WON: set(),
    TenderStatus.LOST: set(),
}


def validate_status_transition(current_status: str, new_status: str) -> None:
    """Validate tender status transition"""

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    if new_status not in allowed_statuses:
        raise ValidationError(
            f"Invalid status transition: {current_status} → {new_status}"
        )


@transaction.atomic
def change_tender_status(
    tender: Tender,
    new_status: str,
    changed_by,
    reason: str,
) -> Tender:
    """Change tender status and create history record"""

    validate_status_transition(tender.status, new_status)

    old_status = tender.status
    tender.status = new_status
    tender.save(update_fields=["status", "updated_at"])

    TenderStatusHistory.objects.create(
        tender=tender,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
    )

    return tender
