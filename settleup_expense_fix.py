# =============================================================================
# ./expenses/forms.py
# =============================================================================
from django import forms
from django.forms import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError
from expenses.models import Expense, ExpenseSplit, Category


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("description", "amount", "category", "date", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ExpenseSplitForm(forms.Form):
    """
    A plain Form (not ModelForm) so it works for both creation
    and editing without requiring an existing Expense instance.
    """
    group_member_id = forms.IntegerField(widget=forms.HiddenInput)
    member_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
    )
    include = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["percentage"].widget.attrs.update({
            "class": "form-input pr-7 text-sm split-pct",
            "step": "0.01",
        })


class BaseExpenseSplitFormSet(BaseFormSet):

    def clean(self):
        if any(self.errors):
            return

        active_forms = [
            f for f in self.forms
            if f.cleaned_data and f.cleaned_data.get("include")
        ]

        if not active_forms:
            raise ValidationError("At least one member must be included.")

        total = sum(f.cleaned_data.get("percentage", 0) for f in active_forms)

        if round(float(total), 2) != 100.00:
            raise ValidationError(
                f"Percentages must sum to 100. Current total: {total}."
            )

    def get_splits(self):
        """
        Returns a list of dicts for included members.
        Call this after is_valid().
        """
        from groups.models import GroupMember
        splits = []
        for f in self.forms:
            if f.cleaned_data and f.cleaned_data.get("include"):
                member = GroupMember.objects.get(
                    pk=f.cleaned_data["group_member_id"]
                )
                splits.append({
                    "group_member": member,
                    "percentage": f.cleaned_data["percentage"],
                })
        return splits


ExpenseSplitFormSet = formset_factory(
    ExpenseSplitForm,
    formset=BaseExpenseSplitFormSet,
    extra=0,
)


# =============================================================================
# ./expenses/views.py
# =============================================================================
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


def _build_split_initial(group):
    """
    Builds initial formset data from active members' default percentages.
    """
    members = GroupMember.objects.filter(
        group=group,
        status=GroupMember.Status.ACTIVE,
    ).select_related("user").order_by("user__first_name")

    return [
        {
            "group_member_id": m.pk,
            "member_name": m.user.get_full_name(),
            "percentage": m.default_percentage,
            "include": True,
        }
        for m in members
    ]


def _build_split_initial_from_expense(expense):
    """
    Builds initial formset data from an existing expense's splits,
    including active members not currently in the split.
    """
    existing = {
        s.group_member_id: s.percentage
        for s in expense.splits.select_related("group_member__user")
    }
    active_members = GroupMember.objects.filter(
        group=expense.group,
        status=GroupMember.Status.ACTIVE,
    ).select_related("user").order_by("user__first_name")

    return [
        {
            "group_member_id": m.pk,
            "member_name": m.user.get_full_name(),
            "percentage": existing.get(m.pk, m.default_percentage),
            "include": m.pk in existing,
        }
        for m in active_members
    ]


class ExpenseCreateView(ActiveMemberRequiredMixin, View):
    template_name = "expenses/expense_form.html"

    def get(self, request, group_id):
        form = ExpenseForm()
        initial = _build_split_initial(self.group)
        formset = ExpenseSplitFormSet(initial=initial)
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
        })

    def post(self, request, group_id):
        form = ExpenseForm(request.POST)
        initial = _build_split_initial(self.group)
        formset = ExpenseSplitFormSet(request.POST, initial=initial)

        if form.is_valid() and formset.is_valid():
            try:
                create_expense(
                    group=self.group,
                    paid_by=self.group_member,
                    created_by=self.group_member,
                    form_data=form.cleaned_data,
                    splits=formset.get_splits(),
                )
                messages.success(request, "Expense added.")
                return redirect("expense_list", group_id=self.group.pk)
            except Exception as e:
                messages.error(request, str(e))

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
        })


class ExpenseEditView(ActiveMemberRequiredMixin, View):
    template_name = "expenses/expense_form.html"

    def get_expense(self):
        expense = get_object_or_404(
            Expense, pk=self.kwargs["expense_id"], group=self.group
        )
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
        initial = _build_split_initial_from_expense(expense)
        formset = ExpenseSplitFormSet(initial=initial)
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
            "expense": expense,
        })

    def post(self, request, group_id, expense_id):
        expense = self.get_expense()
        form = ExpenseForm(request.POST, instance=expense)
        initial = _build_split_initial_from_expense(expense)
        formset = ExpenseSplitFormSet(request.POST, initial=initial)

        if form.is_valid() and formset.is_valid():
            try:
                edit_expense(
                    expense=expense,
                    form_data=form.cleaned_data,
                    splits=formset.get_splits(),
                )
                messages.success(request, "Expense updated.")
                return redirect("expense_list", group_id=self.group.pk)
            except Exception as e:
                messages.error(request, str(e))

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "group": self.group,
            "expense": expense,
        })


class ExpenseDeleteView(AdminRequiredMixin, View):
    def post(self, request, group_id, expense_id):
        expense = get_object_or_404(
            Expense, pk=expense_id, group=self.group
        )
        delete_expense(expense, self.group_member)
        messages.success(request, "Expense deleted.")
        return redirect("expense_list", group_id=self.group.pk)


# =============================================================================
# ./templates/expenses/expense_form.html
# =============================================================================
{% extends "base.html" %}
{% block title %}{% if expense %}Edit Expense{% else %}Add Expense{% endif %} — SettleUp{% endblock %}
{% block page_title %}{% if expense %}Edit Expense{% else %}Add Expense{% endif %}{% endblock %}
{% block nav_expenses %}active{% endblock %}
{% block content %}
<div class="max-w-xl">
  <form method="post" id="expenseForm">
    {% csrf_token %}
    {{ formset.management_form }}

    <div class="card p-6 space-y-5 mb-4">
      <h2 class="font-semibold text-ink text-sm border-b border-surface-border pb-3">Expense Details</h2>
      <div>
        <label class="form-label">Description</label>
        <input type="text" name="description" class="form-input"
               placeholder="e.g. Groceries, Electricity bill"
               value="{{ form.description.value|default:'' }}" />
        {% if form.description.errors %}<p class="text-xs text-red-400 mt-1">{{ form.description.errors|join:", " }}</p>{% endif %}
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="form-label">Amount</label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-dim">$</span>
            <input type="number" name="amount" step="0.01" min="0.01"
                   class="form-input pl-7"
                   value="{{ form.amount.value|default:'' }}" />
          </div>
          {% if form.amount.errors %}<p class="text-xs text-red-400 mt-1">{{ form.amount.errors|join:", " }}</p>{% endif %}
        </div>
        <div>
          <label class="form-label">Date</label>
          <input type="date" name="date" class="form-input"
                 value="{{ form.date.value|default:'' }}" />
          {% if form.date.errors %}<p class="text-xs text-red-400 mt-1">{{ form.date.errors|join:", " }}</p>{% endif %}
        </div>
      </div>
      <div>
        <label class="form-label">Category</label>
        <select name="category" class="form-input">
          <option value="">— Select category —</option>
          {% for cat in form.fields.category.queryset %}
          <option value="{{ cat.pk }}"
            {% if form.category.value == cat.pk|stringformat:"s" %}selected{% endif %}>
            {{ cat.name }}
          </option>
          {% endfor %}
        </select>
        {% if form.category.errors %}<p class="text-xs text-red-400 mt-1">{{ form.category.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Notes <span class="normal-case font-normal text-ink-dim">(optional)</span></label>
        <textarea name="notes" class="form-input">{{ form.notes.value|default:'' }}</textarea>
      </div>
    </div>

    <!-- Splits -->
    <div class="card p-6 space-y-4 mb-4">
      <div class="flex items-center justify-between border-b border-surface-border pb-3">
        <h2 class="font-semibold text-ink text-sm">Split</h2>
        <span class="text-xs text-ink-dim">
          Total: <span id="splitTotal" class="font-mono font-semibold text-red-400">0%</span>
        </span>
      </div>

      <div class="space-y-3">
        {% for f in formset %}
        <div class="split-row flex items-center gap-3">
          <input type="hidden" name="{{ f.group_member_id.html_name }}"
                 value="{{ f.group_member_id.value }}" />
          <span class="flex-1 text-sm text-ink">{{ f.member_name.value }}</span>
          <div class="w-28 relative">
            <input type="number"
                   name="{{ f.percentage.html_name }}"
                   step="0.01" min="0" max="100"
                   class="form-input pr-7 text-sm split-pct"
                   value="{{ f.percentage.value|default:'' }}" />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim text-xs">%</span>
          </div>
          <label class="flex items-center gap-1.5 text-xs text-ink-dim cursor-pointer whitespace-nowrap">
            <input type="checkbox"
                   name="{{ f.include.html_name }}"
                   class="rounded border-surface-border delete-check"
                   {% if f.include.value %}checked{% endif %} />
            Include
          </label>
        </div>
        {% if f.errors %}
        <p class="text-xs text-red-400 pl-2">{{ f.errors }}</p>
        {% endif %}
        {% endfor %}
      </div>

      {% if formset.non_form_errors %}
      <p class="text-xs text-red-400 mt-2">{{ formset.non_form_errors|join:", " }}</p>
      {% endif %}
    </div>

    <div class="flex gap-3">
      <button type="submit" class="btn-primary">
        {% if expense %}Save changes{% else %}Add expense{% endif %}
      </button>
      <a href="{% url 'expense_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
    </div>
  </form>
</div>

<script>
  function updateSplitTotal() {
    const rows = document.querySelectorAll('.split-row');
    let total = 0;
    rows.forEach(row => {
      const check = row.querySelector('.delete-check');
      const pct = row.querySelector('.split-pct');
      if (check && check.checked && pct) {
        total += parseFloat(pct.value) || 0;
      }
    });
    const el = document.getElementById('splitTotal');
    el.textContent = total.toFixed(2) + '%';
    el.className = 'font-mono font-semibold ' +
      (Math.abs(total - 100) < 0.01 ? 'text-accent' : 'text-red-400');
  }
  document.addEventListener('input', updateSplitTotal);
  document.addEventListener('change', updateSplitTotal);
  updateSplitTotal();
</script>
{% endblock %}
