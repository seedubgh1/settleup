from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import View
from expenses.models import Expense, ExpenseSplit, Category
from groups.mixins import ActiveMemberRequiredMixin


class ReportView(ActiveMemberRequiredMixin, View):
    template_name = "reporting/report.html"

    def get(self, request, group_id):
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        category_id = request.GET.get("category")

        qs = ExpenseSplit.objects.filter(
            expense__group=self.group,
            expense__is_deleted=False,
        )
        if date_from:
            qs = qs.filter(expense__date__gte=date_from)
        if date_to:
            qs = qs.filter(expense__date__lte=date_to)
        if category_id:
            qs = qs.filter(expense__category_id=category_id)

        by_category = (
            qs.values("expense__category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        return render(request, self.template_name, {
            "group": self.group,
            "by_category": by_category,
            "categories": Category.objects.all(),
            "date_from": date_from,
            "date_to": date_to,
            "selected_category": category_id,
        })
