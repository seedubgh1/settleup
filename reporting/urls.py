from django.urls import path
from reporting import views

urlpatterns = [
    path("", views.ReportView.as_view(), name="report"),
]
