from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
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


class ExpenseSplitForm(forms.ModelForm):
    class Meta:
        model = ExpenseSplit
        fields = ("group_member", "percentage")

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            from groups.models import GroupMember
            self.fields["group_member"].queryset = GroupMember.objects.filter(
                group=group,
                status=GroupMember.Status.ACTIVE,
            ).select_related("user")
            self.fields["group_member"].label_from_instance = (
                lambda m: m.user.get_full_name()
            )


class BaseExpenseSplitFormSet(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            return

        active_forms = [
            f for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]

        if not active_forms:
            raise ValidationError("At least one split is required.")

        total_percentage = 0
        for form in active_forms:
            pct = form.cleaned_data.get("percentage", 0)
            if pct <= 0:
                raise ValidationError(
                    "Each split percentage must be greater than 0."
                )
            total_percentage += pct

        if round(total_percentage, 2) != 100.00:
            raise ValidationError(
                f"Split percentages must sum to 100. Current total: {total_percentage}."
            )


ExpenseSplitFormSet = inlineformset_factory(
    parent_model=Expense,
    model=ExpenseSplit,
    form=ExpenseSplitForm,
    formset=BaseExpenseSplitFormSet,
    fields=("group_member", "percentage"),
    extra=0,
    can_delete=True,
)
