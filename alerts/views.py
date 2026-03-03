from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View
from alerts.models import Alert
from alerts.services import mark_alert_read


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = "alerts/alert_list.html"
    context_object_name = "alerts"
    paginate_by = 20

    def get_queryset(self):
        return Alert.objects.filter(
            recipient__user=self.request.user,
        ).select_related("recipient__group")


class AlertMarkReadView(LoginRequiredMixin, View):
    def post(self, request, alert_id):
        alert = get_object_or_404(
            Alert,
            pk=alert_id,
            recipient__user=request.user,
        )
        mark_alert_read(alert)
        return redirect(request.META.get("HTTP_REFERER", "alert_list"))
