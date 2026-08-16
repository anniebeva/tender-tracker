from django.conf import settings
from django.db import models


class TenderStatus(models.TextChoices):
    """Available tender statuses"""

    DRAFT = "draft", "Черновик"
    ACTIVE = "active", "Активен"
    WON = "won", "Выигран"
    LOST = "lost", "Проигран"


class Tender(models.Model):
    """Tender model"""

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=TenderStatus.choices,
        default=TenderStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tenders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return tender title"""

        return self.title


class TenderStatusHistory(models.Model):
    """Tender status change history"""

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    old_status = models.CharField(
        max_length=10,
        choices=TenderStatus.choices,
    )
    new_status = models.CharField(
        max_length=10,
        choices=TenderStatus.choices,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tender_status_changes",
    )
    reason = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        """Return status change description"""

        return f"{self.tender} — {self.old_status} → {self.new_status}"
