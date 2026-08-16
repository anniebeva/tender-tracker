from django.contrib import admin

from .models import Tender, TenderStatusHistory


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    """Configure tender administration"""

    list_display = (
        "title",
        "status",
        "created_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TenderStatusHistory)
class TenderStatusHistoryAdmin(admin.ModelAdmin):
    """Configure tender status history administration"""

    list_display = (
        "tender",
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
    )
    list_filter = ("old_status", "new_status", "changed_at")
    search_fields = (
        "tender__title",
        "reason",
        "changed_by__username",
    )
    readonly_fields = ("changed_at",)
