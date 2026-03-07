import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View
from payments.models import Payment
from payments.forms import PaymentForm
from groups.mixins import ActiveMemberRequiredMixin, AdminRequiredMixin, GroupMemberRequiredMixin


class PaymentListView(GroupMemberRequiredMixin, ListView):
    template_name = "payments/payment_list.html"
    context_object_name = "payments"
    paginate_by = 25

    def get_queryset(self):
        qs = Payment.objects.filter(
            group=self.group,
        ).select_related("paid_by__user")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        member = self.request.GET.get("member")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if member:
            qs = qs.filter(paid_by_id=member)
        return qs


class PaymentCreateView(ActiveMemberRequiredMixin, View):
    template_name = "payments/payment_form.html"

    def get(self, request, group_id):
        form = PaymentForm(initial={"date": datetime.date.today()})
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.group = self.group
            payment.paid_by = self.group_member

            # Validate here instead of on the model
            if payment.paid_by.group != payment.group:
                messages.error(request, "The paying member must belong to this group.")
                return render(request, self.template_name, {"form": form, "group": self.group})
            
            payment.save()
            messages.success(request, "Payment recorded.")
            return redirect("payment_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })


class PaymentDeleteView(AdminRequiredMixin, View):
    def post(self, request, group_id, payment_id):
        payment = get_object_or_404(
            Payment, pk=payment_id, group=self.group
        )
        payment.delete()
        messages.success(request, "Payment deleted.")
        return redirect("payment_list", group_id=self.group.pk)
