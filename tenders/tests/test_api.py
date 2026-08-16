import pytest

from tenders.models import Tender, TenderStatus, TenderStatusHistory


@pytest.mark.django_db
class TestTenderAPI:
    """Test tender API endpoints"""

    def test_create_tender(self, api_client, user):
        """Test tender creation"""

        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/tenders/",
            {
                "title": "Test tender",
                "description": "Test description",
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["title"] == "Test tender"
        assert response.data["description"] == "Test description"
        assert response.data["status"] == TenderStatus.DRAFT
        assert response.data["created_by"] == "testuser"

        assert Tender.objects.count() == 1

    def test_get_tender(self, api_client, user):
        """Test tender retrieval"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
        )

        response = api_client.get(f"/api/tenders/{tender.id}/")

        assert response.status_code == 200
        assert response.data["id"] == tender.id
        assert response.data["title"] == "Test tender"
        assert response.data["status"] == TenderStatus.DRAFT
        assert response.data["status_history"] == []

    def test_update_tender_status(self, api_client, user):
        """Test tender status update"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
        )

        response = api_client.patch(
            f"/api/tenders/{tender.id}/status/",
            {
                "status": TenderStatus.ACTIVE,
                "reason": "Tender published",
            },
            format="json",
        )

        assert response.status_code == 200

        tender.refresh_from_db()

        assert tender.status == TenderStatus.ACTIVE

        history = TenderStatusHistory.objects.get(tender=tender)

        assert history.old_status == TenderStatus.DRAFT
        assert history.new_status == TenderStatus.ACTIVE
        assert history.changed_by == user
        assert history.reason == "Tender published"

    def test_get_tender_with_status_history(self, api_client, user):
        """Test tender retrieval with status history"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
        )

        TenderStatusHistory.objects.create(
            tender=tender,
            old_status=TenderStatus.DRAFT,
            new_status=TenderStatus.ACTIVE,
            changed_by=user,
            reason="Tender published",
        )

        response = api_client.get(f"/api/tenders/{tender.id}/")

        assert response.status_code == 200
        assert len(response.data["status_history"]) == 1
        assert response.data["status_history"][0]["old_status"] == TenderStatus.DRAFT
        assert response.data["status_history"][0]["new_status"] == TenderStatus.ACTIVE
        assert response.data["status_history"][0]["changed_by"] == "testuser"

    def test_create_tender_requires_authentication(self, api_client):
        """Test tender creation requires authentication"""

        response = api_client.post(
            "/api/tenders/",
            {
                "title": "Test tender",
                "description": "Test description",
            },
            format="json",
        )

        assert response.status_code == 401

    def test_get_tender_requires_authentication(self, api_client, user):
        """Test tender retrieval requires authentication"""

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
        )

        response = api_client.get(f"/api/tenders/{tender.id}/")

        assert response.status_code == 401

    def test_invalid_status_transition(self, api_client, user):
        """Test invalid tender status transition"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
        )

        response = api_client.patch(
            f"/api/tenders/{tender.id}/status/",
            {
                "status": TenderStatus.WON,
                "reason": "Invalid transition",
            },
            format="json",
        )

        assert response.status_code == 400

        tender.refresh_from_db()

        assert tender.status == TenderStatus.DRAFT
        assert TenderStatusHistory.objects.count() == 0
