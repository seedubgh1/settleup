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
