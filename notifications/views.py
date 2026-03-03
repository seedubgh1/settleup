from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, View
from notifications.models import Notification
from notifications.services import generate_notifications
from groups.mixins import AdminRequiredMixin


class NotificationListView(AdminRequiredMixin, ListView):
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 25

    def get_queryset(self):
        return Notification.objects.filter(
            group=self.group,
        ).select_related("recipient__user", "triggered_by__user")


class NotificationSendView(AdminRequiredMixin, View):
    def post(self, request, group_id):
        notifications = generate_notifications(
            self.group,
            triggered_by=self.group_member,
        )
        count = len(notifications)
        messages.success(
            request,
            f"{count} notification(s) queued for delivery."
        )
        return redirect("notification_list", group_id=self.group.pk)
