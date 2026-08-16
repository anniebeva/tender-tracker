from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tender
from .serializers import (
    TenderDetailSerializer,
    TenderSerializer,
    TenderStatusUpdateSerializer,
)
from .services import change_tender_status


class TenderCreateView(APIView):
    """Create a new tender"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TenderSerializer,
        responses={201: TenderSerializer},
    )
    def post(self, request):
        """Handle tender creation request"""

        serializer = TenderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tender = serializer.save(created_by=request.user)

        return Response(
            TenderSerializer(tender).data,
            status=status.HTTP_201_CREATED,
        )


class TenderDetailView(APIView):
    """Retrieve a tender with its status history"""

    permission_classes = [IsAuthenticated]
    serializer_class = TenderDetailSerializer

    @extend_schema(
        responses=TenderDetailSerializer,
    )
    def get(self, request, pk):
        """Handle tender retrieval request"""

        tender = get_object_or_404(Tender, pk=pk)

        serializer = TenderDetailSerializer(tender)

        return Response(serializer.data)


class TenderStatusUpdateView(APIView):
    """Update tender status"""

    permission_classes = [IsAuthenticated]
    serializer_class = TenderStatusUpdateSerializer

    @extend_schema(
        request=TenderStatusUpdateSerializer,
        responses={200: TenderSerializer},
    )
    def patch(self, request, pk):
        """Handle tender status update request"""

        tender = get_object_or_404(Tender, pk=pk)

        serializer = TenderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tender = change_tender_status(
                tender=tender,
                new_status=serializer.validated_data["status"],
                changed_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValidationError as exc:
            return Response(
                {"detail": str(exc.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(TenderSerializer(tender).data)
