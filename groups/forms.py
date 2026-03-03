from django import forms
from django.core.exceptions import ValidationError
from groups.models import Group, GroupMember, Invitation


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "description")


class GroupMemberEditForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ("role", "default_percentage")

    def clean_default_percentage(self):
        pct = self.cleaned_data["default_percentage"]
        if pct <= 0 or pct > 100:
            raise ValidationError(
                "Percentage must be greater than 0 and no more than 100."
            )
        return pct


class RebalanceForm(forms.Form):
    """
    Dynamically generated — one percentage field per active member.
    Instantiated with members= kwarg in the view.
    """
    def __init__(self, *args, members, **kwargs):
        super().__init__(*args, **kwargs)
        for member in members:
            self.fields[f"pct_{member.pk}"] = forms.DecimalField(
                label=member.user.get_full_name(),
                initial=member.default_percentage,
                max_digits=5,
                decimal_places=2,
                min_value=0,
                max_value=100,
            )
        self.members = members

    def clean(self):
        cleaned = super().clean()
        total = sum(
            cleaned.get(f"pct_{m.pk}", 0) for m in self.members
        )
        if round(total, 2) != 100.00:
            raise ValidationError(
                f"Percentages must sum to 100. Current total: {total}."
            )
        return cleaned


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ("email", "default_percentage")

    def __init__(self, *args, group, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

    def clean_email(self):
        email = self.cleaned_data["email"]
        if GroupMember.objects.filter(
            group=self.group,
            user__email=email,
            status=GroupMember.Status.ACTIVE,
        ).exists():
            raise ValidationError(
                "This person is already an active member of the group."
            )
        if Invitation.objects.filter(
            group=self.group,
            email=email,
            status=Invitation.Status.PENDING,
        ).exists():
            raise ValidationError(
                "A pending invitation already exists for this email."
            )
        return email

    def clean_default_percentage(self):
        pct = self.cleaned_data["default_percentage"]
        if pct <= 0 or pct > 100:
            raise ValidationError(
                "Percentage must be greater than 0 and no more than 100."
            )
        return pct


class TransferOwnershipForm(forms.Form):
    new_owner = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, group, current_owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_owner"].queryset = GroupMember.objects.filter(
            group=group,
            status=GroupMember.Status.ACTIVE,
        ).exclude(pk=current_owner.pk).select_related("user")
        self.fields["new_owner"].label_from_instance = (
            lambda m: m.user.get_full_name()
        )
