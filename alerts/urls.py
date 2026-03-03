from django.urls import path
from alerts import views

urlpatterns = [
    path("", views.AlertListView.as_view(), name="alert_list"),
    path("<int:alert_id>/read/", views.AlertMarkReadView.as_view(),
         name="alert_mark_read"),
]
