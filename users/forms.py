from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)


    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username to keep Django auth happy
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class ProfileForm(UserChangeForm):
    password = None  # Remove password field from profile edit

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
