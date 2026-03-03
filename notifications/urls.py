from django.urls import path
from notifications import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("send/", views.NotificationSendView.as_view(), name="notification_send"),
]
