from django.urls import path

from .views import(
    TenderCreateView,
    TenderDetailView,
    TenderStatusUpdateView,
    TenderListView,
)


urlpatterns = [
    path("", TenderCreateView.as_view(), name="tender-create"),
    path("list/", TenderListView.as_view(), name="tender-list"),
    path("<int:pk>/", TenderDetailView.as_view(), name="tender-detail"),
    path(
        "<int:pk>/status/",
        TenderStatusUpdateView.as_view(),
        name="tender-status-update",
    ),
]
