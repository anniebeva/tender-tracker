from rest_framework import serializers

from .models import Tender, TenderStatus, TenderStatusHistory


class TenderSerializer(serializers.ModelSerializer):
    """Serialize tender data"""

    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Tender
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )


class TenderStatusUpdateSerializer(serializers.Serializer):
    """Validate tender status update data"""

    status = serializers.ChoiceField(choices=TenderStatus.choices)
    reason = serializers.CharField()


class TenderStatusHistorySerializer(serializers.ModelSerializer):
    """Serialize tender status history"""

    changed_by = serializers.ReadOnlyField(source="changed_by.username")

    class Meta:
        model = TenderStatusHistory
        fields = (
            "id",
            "old_status",
            "new_status",
            "changed_by",
            "reason",
            "changed_at",
        )


class TenderDetailSerializer(TenderSerializer):
    """Serialize tender with status history"""

    status_history = TenderStatusHistorySerializer(
        many=True,
        read_only=True,
    )

    class Meta(TenderSerializer.Meta):
        fields = TenderSerializer.Meta.fields + ("status_history",)
