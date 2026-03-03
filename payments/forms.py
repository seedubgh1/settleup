from django import forms
from payments.models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "date", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
