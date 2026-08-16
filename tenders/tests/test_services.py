import pytest
from django.core.exceptions import ValidationError

from tenders.models import Tender, TenderStatus, TenderStatusHistory
from tenders.services import change_tender_status


@pytest.mark.django_db
def test_change_tender_status_to_active(user):
    """Change tender status from draft to active"""

    tender = Tender.objects.create(
        title="Test tender",
        description="Test description",
        created_by=user,
    )

    change_tender_status(
        tender=tender,
        new_status=TenderStatus.ACTIVE,
        changed_by=user,
        reason="Tender published",
    )

    tender.refresh_from_db()

    assert tender.status == TenderStatus.ACTIVE

    history = TenderStatusHistory.objects.get(tender=tender)

    assert history.old_status == TenderStatus.DRAFT
    assert history.new_status == TenderStatus.ACTIVE
    assert history.changed_by == user
    assert history.reason == "Tender published"


@pytest.mark.django_db
def test_change_tender_status_to_won(user):
    """Change tender status from active to won"""

    tender = Tender.objects.create(
        title="Test tender",
        description="Test description",
        status=TenderStatus.ACTIVE,
        created_by=user,
    )

    change_tender_status(
        tender=tender,
        new_status=TenderStatus.WON,
        changed_by=user,
        reason="Tender won",
    )

    tender.refresh_from_db()

    assert tender.status == TenderStatus.WON


@pytest.mark.django_db
def test_change_tender_status_to_lost(user):
    """Change tender status from active to lost"""

    tender = Tender.objects.create(
        title="Test tender",
        description="Test description",
        status=TenderStatus.ACTIVE,
        created_by=user,
    )

    change_tender_status(
        tender=tender,
        new_status=TenderStatus.LOST,
        changed_by=user,
        reason="Tender lost",
    )

    tender.refresh_from_db()

    assert tender.status == TenderStatus.LOST


@pytest.mark.django_db
def test_invalid_status_transition(user):
    """Reject invalid tender status transition"""

    tender = Tender.objects.create(
        title="Test tender",
        description="Test description",
        created_by=user,
    )

    with pytest.raises(ValidationError):
        change_tender_status(
            tender=tender,
            new_status=TenderStatus.WON,
            changed_by=user,
            reason="Invalid transition",
        )

    tender.refresh_from_db()

    assert tender.status == TenderStatus.DRAFT
    assert not TenderStatusHistory.objects.filter(tender=tender).exists()
