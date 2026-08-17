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

    def test_create_tender_requires_title(self, api_client, user):
        """Test tender creation requires title"""

        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/tenders/",
            {
                "description": "Test description",
            },
            format="json",
        )

        assert response.status_code == 400
        assert "title" in response.data

    def test_create_tender_rejects_empty_title(self, api_client, user):
        """Test tender creation rejects empty title"""

        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/tenders/",
            {
                "title": "",
                "description": "Test description",
            },
            format="json",
        )

        assert response.status_code == 400
        assert "title" in response.data

    def test_update_status_requires_reason(self, api_client, user):
        """Test tender status update requires reason"""

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
            },
            format="json",
        )

        assert response.status_code == 400
        assert "reason" in response.data

    def test_get_nonexistent_tender(self, api_client, user):
        """Test retrieval of nonexistent tender"""

        api_client.force_authenticate(user=user)

        response = api_client.get("/api/tenders/999999/")

        assert response.status_code == 404

    def test_update_nonexistent_tender(self, api_client, user):
        """Test status update for nonexistent tender"""

        api_client.force_authenticate(user=user)

        response = api_client.patch(
            "/api/tenders/999999/status/",
            {
                "status": TenderStatus.ACTIVE,
                "reason": "Tender published",
            },
            format="json",
        )

        assert response.status_code == 404

    def test_active_tender_can_be_won(self, api_client, user):
        """Test active tender can be marked as won"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
            status=TenderStatus.ACTIVE,
        )

        response = api_client.patch(
            f"/api/tenders/{tender.id}/status/",
            {
                "status": TenderStatus.WON,
                "reason": "Tender won",
            },
            format="json",
        )

        assert response.status_code == 200

        tender.refresh_from_db()

        assert tender.status == TenderStatus.WON

    def test_active_tender_can_be_lost(self, api_client, user):
        """Test active tender can be marked as lost"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
            status=TenderStatus.ACTIVE,
        )

        response = api_client.patch(
            f"/api/tenders/{tender.id}/status/",
            {
                "status": TenderStatus.LOST,
                "reason": "Tender lost",
            },
            format="json",
        )

        assert response.status_code == 200

        tender.refresh_from_db()

        assert tender.status == TenderStatus.LOST

    def test_won_tender_cannot_change_status(self, api_client, user):
        """Test won tender cannot change status"""

        api_client.force_authenticate(user=user)

        tender = Tender.objects.create(
            title="Test tender",
            description="Test description",
            created_by=user,
            status=TenderStatus.WON,
        )

        response = api_client.patch(
            f"/api/tenders/{tender.id}/status/",
            {
                "status": TenderStatus.LOST,
                "reason": "Try to change completed tender",
            },
            format="json",
        )

        assert response.status_code == 400

        tender.refresh_from_db()

        assert tender.status == TenderStatus.WON

    def test_get_tenders(self, api_client, user):
        """Test tender list retrieval"""

        api_client.force_authenticate(user=user)

        Tender.objects.create(
            title="First tender",
            description="First description",
            created_by=user,
        )
        Tender.objects.create(
            title="Second tender",
            description="Second description",
            created_by=user,
        )

        response = api_client.get("/api/tenders/list/")

        assert response.status_code == 200
        assert len(response.data) == 2
        assert response.data[0]["title"] == "Second tender"
        assert response.data[1]["title"] == "First tender"

    def test_get_tenders_requires_authentication(self, api_client):
        """Test tender list requires authentication"""

        response = api_client.get("/api/tenders/list/")

        assert response.status_code == 401

    def test_get_tenders_by_status(self, api_client, user):
        """Test tender list filtering by status"""

        api_client.force_authenticate(user=user)

        Tender.objects.create(
            title="Draft tender",
            description="Draft description",
            created_by=user,
        )

        active_tender = Tender.objects.create(
            title="Active tender",
            description="Active description",
            created_by=user,
            status=TenderStatus.ACTIVE,
        )

        response = api_client.get("/api/tenders/list/?status=active")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == active_tender.id
        assert response.data[0]["status"] == TenderStatus.ACTIVE
