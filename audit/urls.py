from django.urls import path
from audit import views

urlpatterns = [
    path("", views.AuditLogView.as_view(), name="audit_log"),
]
