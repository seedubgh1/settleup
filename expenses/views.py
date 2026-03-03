from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from expenses.models import Expense, Category
from expenses.forms import ExpenseForm, ExpenseSplitFormSet
from expenses.services import create_expense, edit_expense, delete_expense
from groups.mixins import ActiveMemberRequiredMixin, AdminRequiredMixin
from groups.models import GroupMember


class ExpenseListView(ActiveMemberRequiredMixin, ListView):
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"
    paginate_by = 25

    def get_queryset(self):
        show_deleted = (
            self.request.GET.get("show_deleted") == "true"
            and self.group_member.role in [
                GroupMember.Role.ADMIN, GroupMember.Role.OWNER
            ]
        )
        qs = Expense.objects.filter(group=self.group)
        if not show_deleted:
            qs = qs.filter(is_deleted=False)
        # Filters
        category = self.request.GET.get("category")
        member = self.request.GET.get("member")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        if category:
            qs = qs.filter(category_id=category)
        if member:
            qs = qs.filter(splits__group_member_id=member)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs.select_related(
            "paid_by__user", "category", "created_by__user"
        ).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["members"] = GroupMember.objects.filter(
            group=self.group
        ).select_related("user")
        ctx["show_deleted"] = (
            self.request.GET.get("show_deleted") == "true"
            and self.group_member.role in [
                GroupMember.Role.ADMIN, GroupMember.Role.OWNER
            ]
        )
        return ctx


class ExpenseDetailView(ActiveMemberRequiredMixin, DetailView):
    template_name = "expenses/expense_detail.html"
    context_object_name = "expense"

    def get_object(self):
        return get_object_or_404(
            Expense,
            pk=self.kwargs["expense_id"],
            group=self.group,
        )


class ExpenseCreateView(ActiveMemberRequiredMixin, View):
    template_name = "expenses/expense_form.html"

    def _initial_splits(self):
        """Build initial split data from active members' default percentages."""
        members = GroupMember.objects.filter(
            group=self.group,
            status=GroupMember.Status.ACTIVE,
        ).select_related("user")
        return [
            {"group_member": m, "percentage": m.default_percentage}
            for m in members
        ]

    def get(self, request, group_id):
        form = ExpenseForm()
        formset = ExpenseSplitFormSet(
            queryset=ExpenseSplitFormSet.model.objects.none(),
        )
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
            "initial_splits": self._initial_splits(),
        })

    def post(self, request, group_id):
        form = ExpenseForm(request.POST)
        formset = ExpenseSplitFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            splits = [
                {
                    "group_member": f.cleaned_data["group_member"],
                    "percentage": f.cleaned_data["percentage"],
                }
                for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            from django.core.exceptions import ValidationError
            try:
                create_expense(
                    group=self.group,
                    paid_by=self.group_member,
                    created_by=self.group_member,
                    form_data=form.cleaned_data,
                    splits=splits,
                )
                messages.success(request, "Expense added.")
                return redirect("expense_list", group_id=self.group.pk)
            except ValidationError as e:
                messages.error(request, e.message)
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
            "initial_splits": self._initial_splits(),
        })


class ExpenseEditView(ActiveMemberRequiredMixin, View):
    template_name = "expenses/expense_form.html"

    def get_expense(self):
        expense = get_object_or_404(
            Expense, pk=self.kwargs["expense_id"], group=self.group
        )
        # Only creator, admin, or owner can edit
        is_creator = expense.created_by == self.group_member
        is_admin = self.group_member.role in [
            GroupMember.Role.ADMIN, GroupMember.Role.OWNER
        ]
        if not (is_creator or is_admin):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return expense

    def get(self, request, group_id, expense_id):
        expense = self.get_expense()
        form = ExpenseForm(instance=expense)
        formset = ExpenseSplitFormSet(instance=expense)
        return render(request, self.template_name, {
            "form": form, "formset": formset,
            "group": self.group, "expense": expense,
        })

    def post(self, request, group_id, expense_id):
        expense = self.get_expense()
        form = ExpenseForm(request.POST, instance=expense)
        formset = ExpenseSplitFormSet(request.POST, instance=expense)
        if form.is_valid() and formset.is_valid():
            splits = [
                {
                    "group_member": f.cleaned_data["group_member"],
                    "percentage": f.cleaned_data["percentage"],
                }
                for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            from django.core.exceptions import ValidationError
            try:
                edit_expense(expense, form.cleaned_data, splits)
                messages.success(request, "Expense updated.")
                return redirect("expense_list", group_id=self.group.pk)
            except ValidationError as e:
                messages.error(request, e.message)
        return render(request, self.template_name, {
            "form": form, "formset": formset,
            "group": self.group, "expense": expense,
        })


class ExpenseDeleteView(AdminRequiredMixin, View):
    def post(self, request, group_id, expense_id):
        expense = get_object_or_404(
            Expense, pk=expense_id, group=self.group
        )
        delete_expense(expense, self.group_member)
        messages.success(request, "Expense deleted.")
        return redirect("expense_list", group_id=self.group.pk)
