# =============================================================================
# settleup — Bootstrap Files
# =============================================================================
# Each section is preceded by a comment with the full path relative to the
# project root. Create or replace each file at that location.
# =============================================================================


# =============================================================================
# ./manage.py
# =============================================================================
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# =============================================================================
# ./.env
# =============================================================================
# NOTE: This is not a Python file — save it as .env in the project root.
# Update DATABASE_URL with your actual PostgreSQL credentials.
# Replace SECRET_KEY before deploying to production.
#
# SECRET_KEY=django-insecure-0_n%12*25m)%nh!vn=f6dh*(6^hyuw8i3&wl5=eu$2+&_jv+zs
# DEBUG=True
# DATABASE_URL=postgres://postgres:postgres@localhost:5432/settleup
# ALLOWED_HOSTS=localhost,127.0.0.1
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# DEFAULT_FROM_EMAIL=noreply@settleup.app
# INVITATION_EXPIRY_DAYS=7


# =============================================================================
# ./config/settings/__init__.py
# =============================================================================
# intentionally empty


# =============================================================================
# ./config/settings/base.py
# =============================================================================
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "crispy_forms",
    "crispy_bootstrap5",
]

LOCAL_APPS = [
    "users",
    "groups",
    "expenses",
    "payments",
    "notifications",
    "alerts",
    "audit",
    "reporting",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "alerts.context_processors.unread_alert_count",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL")
}

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/groups/"
LOGOUT_REDIRECT_URL = "/login/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@settleup.app")

INVITATION_EXPIRY_DAYS = env.int("INVITATION_EXPIRY_DAYS", default=7)


# =============================================================================
# ./config/settings/development.py
# =============================================================================
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]


# =============================================================================
# ./config/settings/production.py
# =============================================================================
from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


# =============================================================================
# ./config/urls.py
# =============================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("groups/", include("groups.urls")),
    path("alerts/", include("alerts.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns


# =============================================================================
# ./users/models.py
# =============================================================================
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Email is unique and used as the primary
    identifier for notifications and invitations.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


# =============================================================================
# ./users/urls.py
# =============================================================================
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(
        template_name="users/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset.html",
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html",
    ), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
         ), name="password_reset_confirm"),
    path("password-reset/complete/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="users/password_reset_complete.html",
         ), name="password_reset_complete"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]


# =============================================================================
# ./users/views.py
# =============================================================================
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from users.forms import RegisterForm, ProfileForm
from users.models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("group_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect("group_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user


# =============================================================================
# ./users/forms.py
# =============================================================================
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username to keep Django auth happy
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(UserChangeForm):
    password = None  # Remove password field from profile edit

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


# =============================================================================
# ./users/admin.py
# =============================================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

admin.site.register(User, UserAdmin)


# =============================================================================
# ./alerts/models.py
# =============================================================================
from django.db import models


class Alert(models.Model):

    class AlertType(models.TextChoices):
        PERCENTAGE_CHANGED = "percentage_changed", "Your contribution percentage changed"
        MEMBER_DEACTIVATED = "member_deactivated", "A member was deactivated"
        OWNERSHIP_TRANSFERRED = "ownership_transferred", "Group ownership was transferred"

    recipient = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert for {self.recipient} — {self.alert_type}"


# =============================================================================
# ./alerts/context_processors.py
# =============================================================================
from alerts.models import Alert


def unread_alert_count(request):
    """
    Injects unread_alert_count into every template context.
    Returns 0 if the user is not authenticated.
    """
    if not request.user.is_authenticated:
        return {"unread_alert_count": 0}

    count = Alert.objects.filter(
        recipient__user=request.user,
        is_read=False,
    ).count()

    return {"unread_alert_count": count}


# =============================================================================
# ./alerts/services.py
# =============================================================================
from decimal import Decimal
from django.utils import timezone
from alerts.models import Alert


def alert_percentage_change(
    recipient,
    old_percentage: Decimal,
    new_percentage: Decimal,
    reason: str,
) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.PERCENTAGE_CHANGED,
        message=(
            f"Your default contribution percentage in {recipient.group.name} "
            f"has changed from {old_percentage}% to {new_percentage}%. "
            f"Reason: {reason}"
        ),
    )


def alert_member_deactivated(recipient, deactivated_member) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.MEMBER_DEACTIVATED,
        message=(
            f"{deactivated_member.user.get_full_name()} has been removed "
            f"from {recipient.group.name}."
        ),
    )


def alert_ownership_transferred(recipient, old_owner, new_owner) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.OWNERSHIP_TRANSFERRED,
        message=(
            f"Ownership of {recipient.group.name} has been transferred "
            f"from {old_owner.user.get_full_name()} "
            f"to {new_owner.user.get_full_name()}."
        ),
    )


def mark_alert_read(alert: Alert) -> None:
    alert.is_read = True
    alert.read_at = timezone.now()
    alert.save()


def get_unread_alerts(group_member):
    return Alert.objects.filter(
        recipient=group_member,
        is_read=False,
    )


# =============================================================================
# ./alerts/views.py
# =============================================================================
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


# =============================================================================
# ./alerts/urls.py
# =============================================================================
from django.urls import path
from alerts import views

urlpatterns = [
    path("", views.AlertListView.as_view(), name="alert_list"),
    path("<int:alert_id>/read/", views.AlertMarkReadView.as_view(),
         name="alert_mark_read"),
]


# =============================================================================
# ./alerts/admin.py
# =============================================================================
from django.contrib import admin
from alerts.models import Alert

admin.site.register(Alert)


# =============================================================================
# ./audit/models.py
# =============================================================================
from django.db import models


class AuditLog(models.Model):

    class EventType(models.TextChoices):
        ROLE_CHANGED = "role_changed", "Role Changed"
        PERCENTAGE_CHANGED = "percentage_changed", "Percentage Changed"
        MEMBER_DEACTIVATED = "member_deactivated", "Member Deactivated"
        OWNERSHIP_TRANSFERRED = "ownership_transferred", "Ownership Transferred"
        EXPENSE_DELETED = "expense_deleted", "Expense Deleted"

    group_member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="audit_logs",
        help_text="The member whose record was affected.",
    )
    acted_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="audit_actions",
        help_text="The member who performed the action.",
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"{self.event_type} on {self.group_member} "
            f"by {self.acted_by} at {self.timestamp}"
        )


# =============================================================================
# ./audit/services.py
# =============================================================================
from audit.models import AuditLog


def log_role_change(group_member, acted_by, old_role: str, new_role: str) -> AuditLog:
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.ROLE_CHANGED,
        old_value=old_role,
        new_value=new_role,
    )


def log_percentage_change(
    group_member, acted_by, old_percentage, new_percentage
) -> AuditLog:
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.PERCENTAGE_CHANGED,
        old_value=str(old_percentage),
        new_value=str(new_percentage),
    )


def log_member_deactivation(group_member, acted_by) -> AuditLog:
    from groups.models import GroupMember
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.MEMBER_DEACTIVATED,
        old_value=GroupMember.Status.ACTIVE,
        new_value=GroupMember.Status.INACTIVE,
    )


def log_ownership_transfer(old_owner, new_owner) -> AuditLog:
    return AuditLog.objects.create(
        group_member=new_owner,
        acted_by=old_owner,
        event_type=AuditLog.EventType.OWNERSHIP_TRANSFERRED,
        old_value=old_owner.user.get_full_name(),
        new_value=new_owner.user.get_full_name(),
    )


def log_expense_deletion(expense, deleted_by) -> AuditLog:
    return AuditLog.objects.create(
        group_member=deleted_by,
        acted_by=deleted_by,
        event_type=AuditLog.EventType.EXPENSE_DELETED,
        old_value=str(expense.pk),
        new_value=expense.description,
    )


# =============================================================================
# ./audit/views.py
# =============================================================================
from django.views.generic import ListView
from audit.models import AuditLog
from groups.mixins import ActiveMemberRequiredMixin


class AuditLogView(ActiveMemberRequiredMixin, ListView):
    model = AuditLog
    template_name = "audit/audit_log.html"
    context_object_name = "audit_logs"
    paginate_by = 50

    def get_queryset(self):
        group = self.group  # set by mixin
        member = self.group_member  # set by mixin
        qs = AuditLog.objects.filter(
            group_member__group=group,
        ).select_related("group_member__user", "acted_by__user")

        # Regular members only see events that affected them
        from groups.models import GroupMember
        if member.role == GroupMember.Role.MEMBER:
            qs = qs.filter(group_member=member)

        return qs


# =============================================================================
# ./audit/urls.py
# =============================================================================
from django.urls import path
from audit import views

urlpatterns = [
    path("", views.AuditLogView.as_view(), name="audit_log"),
]


# =============================================================================
# ./audit/admin.py
# =============================================================================
from django.contrib import admin
from audit.models import AuditLog

admin.site.register(AuditLog)


# =============================================================================
# ./groups/models.py
# =============================================================================
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="created_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="group_memberships",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    default_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=(
            "This member's default contribution share. "
            "Active members' percentages must sum to 100."
        ),
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user} in {self.group} ({self.role})"

    def clean(self):
        self._validate_owner_deactivation()

    def _validate_owner_deactivation(self):
        if (
            self.status == self.Status.INACTIVE
            and self.role == self.Role.OWNER
        ):
            raise ValidationError(
                "An owner cannot be deactivated. Transfer ownership first."
            )


class Invitation(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    import uuid as _uuid

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="invitations",
    )
    invited_by = models.ForeignKey(
        GroupMember,
        on_delete=models.PROTECT,
        related_name="invitations_sent",
    )
    email = models.EmailField(
        help_text="Email address of the invitee.",
    )
    token = models.UUIDField(
        default=_uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Unique token for the invitation link.",
    )
    default_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="The percentage assigned to this member upon acceptance.",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="Invitation link expiry. Enforcement handled by the view.",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("group", "email")

    def __str__(self):
        return f"Invitation to {self.email} for {self.group} ({self.status})"


# =============================================================================
# ./groups/mixins.py
# =============================================================================
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from groups.models import Group, GroupMember


class GroupContextMixin(LoginRequiredMixin):
    """
    Base mixin. Resolves the group from the URL and attaches
    self.group and self.group_member to the view.
    """
    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, pk=kwargs["group_id"])
        try:
            self.group_member = GroupMember.objects.get(
                group=self.group,
                user=request.user,
            )
        except GroupMember.DoesNotExist:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["group"] = self.group
        ctx["group_member"] = self.group_member
        return ctx


class GroupMemberRequiredMixin(GroupContextMixin):
    """Any member (active or inactive) of the group."""
    pass


class ActiveMemberRequiredMixin(GroupContextMixin):
    """Only active members."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.status != GroupMember.Status.ACTIVE:
            raise PermissionDenied
        return response


class AdminRequiredMixin(ActiveMemberRequiredMixin):
    """Active admins and owners only."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.role == GroupMember.Role.MEMBER:
            raise PermissionDenied
        return response


class OwnerRequiredMixin(ActiveMemberRequiredMixin):
    """Active owner only."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.role != GroupMember.Role.OWNER:
            raise PermissionDenied
        return response


# =============================================================================
# ./groups/services.py
# =============================================================================
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from groups.models import Group, GroupMember, Invitation


@transaction.atomic
def create_group(name: str, description: str, created_by) -> Group:
    """
    Creates a group and assigns the creator as owner with 100% default
    percentage. 100% because they are the sole active member.
    """
    group = Group.objects.create(
        name=name,
        description=description,
        created_by=created_by,
    )
    GroupMember.objects.create(
        user=created_by,
        group=group,
        role=GroupMember.Role.OWNER,
        default_percentage=Decimal("100.00"),
    )
    return group


@transaction.atomic
def rebalance_percentages(group: Group, percentages: dict) -> None:
    """
    Updates default percentages for active members.
    percentages: {group_member_pk: Decimal}
    Validates sum equals 100 before writing.
    """
    total = sum(percentages.values())
    if round(total, 2) != Decimal("100.00"):
        raise ValidationError(
            f"Percentages must sum to 100. Got {total}."
        )
    for pk, pct in percentages.items():
        GroupMember.objects.filter(pk=pk).update(default_percentage=pct)


@transaction.atomic
def deactivate_member(member: GroupMember, acting_member: GroupMember) -> None:
    """
    Deactivates a member after validating preconditions,
    then auto-rebalances remaining active members.
    Logs the deactivation and percentage changes to the audit log.
    """
    from expenses.services import calculate_balance
    from audit.services import log_member_deactivation
    from alerts.services import alert_member_deactivated

    if member.role == GroupMember.Role.OWNER:
        raise ValidationError("Cannot deactivate the group owner.")

    if acting_member.role == GroupMember.Role.MEMBER:
        raise ValidationError("Members cannot deactivate other members.")

    if (
        acting_member.role == GroupMember.Role.ADMIN
        and member.role == GroupMember.Role.ADMIN
    ):
        raise ValidationError("Admins cannot deactivate other admins.")

    balance = calculate_balance(member)
    if balance != Decimal("0.00"):
        raise ValidationError(
            f"Cannot deactivate {member.user.get_full_name()} — "
            f"outstanding balance of {balance}."
        )

    member.status = GroupMember.Status.INACTIVE
    member.deactivated_at = timezone.now()
    member.save()

    log_member_deactivation(member, acting_member)

    # Notify remaining active members
    active_members = GroupMember.objects.filter(
        group=member.group,
        status=GroupMember.Status.ACTIVE,
    )
    for m in active_members:
        alert_member_deactivated(m, member)

    _auto_rebalance_after_deactivation(member.group, member, acting_member)


def _auto_rebalance_after_deactivation(
    group: Group,
    deactivated_member: GroupMember,
    acted_by: GroupMember,
) -> None:
    """
    Redistributes the deactivated member's percentage proportionally
    across remaining active members.
    """
    from audit.services import log_percentage_change
    from alerts.services import alert_percentage_change

    active_members = list(
        GroupMember.objects.filter(
            group=group,
            status=GroupMember.Status.ACTIVE,
        )
    )

    if not active_members:
        return

    old_percentages = {m.pk: m.default_percentage for m in active_members}
    remaining_total = sum(m.default_percentage for m in active_members)

    if remaining_total == 0:
        even_share = Decimal("100.00") / len(active_members)
        new_percentages = {m.pk: round(even_share, 2) for m in active_members}
    else:
        new_percentages = {
            m.pk: round(
                (m.default_percentage / remaining_total) * Decimal("100.00"), 2
            )
            for m in active_members
        }

    # Correct rounding drift — assign remainder to largest-share member
    total_assigned = sum(new_percentages.values())
    drift = round(Decimal("100.00") - total_assigned, 2)
    if drift != 0:
        largest_pk = max(new_percentages, key=new_percentages.get)
        new_percentages[largest_pk] += drift

    reason = (
        f"{deactivated_member.user.get_full_name()} was removed from the group"
    )

    for m in active_members:
        old_pct = old_percentages[m.pk]
        new_pct = new_percentages[m.pk]
        m.default_percentage = new_pct
        m.save()

        if old_pct != new_pct:
            log_percentage_change(m, acted_by, old_pct, new_pct)
            alert_percentage_change(m, old_pct, new_pct, reason)


@transaction.atomic
def transfer_ownership(
    group: Group,
    current_owner: GroupMember,
    new_owner_member: GroupMember,
) -> None:
    from audit.services import log_ownership_transfer, log_role_change
    from alerts.services import alert_ownership_transferred

    new_owner_member.role = GroupMember.Role.OWNER
    new_owner_member.save()

    current_owner.role = GroupMember.Role.ADMIN
    current_owner.save()

    log_ownership_transfer(current_owner, new_owner_member)
    log_role_change(
        current_owner, current_owner,
        GroupMember.Role.OWNER, GroupMember.Role.ADMIN,
    )

    # Alert all active members
    active_members = GroupMember.objects.filter(
        group=group,
        status=GroupMember.Status.ACTIVE,
    )
    for m in active_members:
        alert_ownership_transferred(m, current_owner, new_owner_member)


@transaction.atomic
def accept_invitation(token: str, user) -> GroupMember:
    """
    Accepts an invitation and creates a GroupMember record.
    """
    from django.core.exceptions import ValidationError

    try:
        invitation = Invitation.objects.select_for_update().get(token=token)
    except Invitation.DoesNotExist:
        raise ValidationError("Invalid invitation link.")

    if invitation.status != Invitation.Status.PENDING:
        raise ValidationError(
            f"This invitation has already been {invitation.status}."
        )

    import django.utils.timezone as tz
    if tz.now() > invitation.expires_at:
        invitation.status = Invitation.Status.EXPIRED
        invitation.save()
        raise ValidationError("This invitation has expired.")

    member = GroupMember.objects.create(
        user=user,
        group=invitation.group,
        role=GroupMember.Role.MEMBER,
        default_percentage=invitation.default_percentage,
    )

    invitation.status = Invitation.Status.ACCEPTED
    invitation.accepted_at = tz.now()
    invitation.save()

    return member


# =============================================================================
# ./groups/forms.py
# =============================================================================
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


# =============================================================================
# ./groups/views.py
# =============================================================================
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View
)
from groups.models import Group, GroupMember, Invitation
from groups.forms import (
    GroupForm, GroupMemberEditForm, RebalanceForm,
    InvitationForm, TransferOwnershipForm,
)
from groups.mixins import (
    ActiveMemberRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin,
    GroupMemberRequiredMixin,
)
from groups.services import (
    create_group, deactivate_member, transfer_ownership, accept_invitation,
    rebalance_percentages,
)
from expenses.services import calculate_group_balances
from django.utils import timezone
from django.conf import settings


class GroupListView(LoginRequiredMixin, ListView):
    template_name = "groups/group_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return GroupMember.objects.filter(
            user=self.request.user,
        ).select_related("group").order_by("-group__created_at")


class GroupCreateView(LoginRequiredMixin, CreateView):
    form_class = GroupForm
    template_name = "groups/group_form.html"

    def form_valid(self, form):
        group = create_group(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            created_by=self.request.user,
        )
        return redirect("group_detail", group_id=group.pk)


class GroupDetailView(ActiveMemberRequiredMixin, DetailView):
    template_name = "groups/group_detail.html"

    def get_object(self):
        return self.group

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from expenses.services import calculate_balance
        from expenses.models import Expense
        ctx["my_balance"] = calculate_balance(self.group_member)
        ctx["recent_expenses"] = (
            Expense.objects
            .filter(group=self.group, is_deleted=False)
            .select_related("paid_by__user", "category")
            .order_by("-date")[:10]
        )
        return ctx


class GroupEditView(OwnerRequiredMixin, UpdateView):
    form_class = GroupForm
    template_name = "groups/group_form.html"

    def get_object(self):
        return self.group

    def get_success_url(self):
        return reverse("group_detail", kwargs={"group_id": self.group.pk})


class GroupArchiveView(OwnerRequiredMixin, View):
    def post(self, request, group_id):
        self.group.is_active = False
        self.group.save()
        messages.success(request, f"{self.group.name} has been archived.")
        return redirect("group_list")


class GroupMemberListView(ActiveMemberRequiredMixin, ListView):
    template_name = "groups/member_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return GroupMember.objects.filter(
            group=self.group,
        ).select_related("user").order_by("status", "user__first_name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["balances"] = calculate_group_balances(self.group)
        return ctx


class MemberInviteView(AdminRequiredMixin, View):
    template_name = "groups/member_invite.html"

    def get_form(self):
        return InvitationForm(
            self.request.POST or None,
            group=self.group,
        )

    def get(self, request, group_id):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": self.get_form(),
            "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        form = self.get_form()
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.group = self.group
            invitation.invited_by = self.group_member
            invitation.expires_at = timezone.now() + timezone.timedelta(
                days=settings.INVITATION_EXPIRY_DAYS
            )
            invitation.save()
            messages.success(
                request,
                f"Invitation recorded for {invitation.email}."
            )
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form,
            "group": self.group,
        })


class GroupMemberEditView(AdminRequiredMixin, View):
    template_name = "groups/member_form.html"

    def get_member(self, member_id):
        return get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )

    def get(self, request, group_id, member_id):
        from django.shortcuts import render
        member = self.get_member(member_id)
        form = GroupMemberEditForm(instance=member)
        return render(request, self.template_name, {
            "form": form, "group": self.group, "member": member,
        })

    def post(self, request, group_id, member_id):
        from django.shortcuts import render
        from audit.services import log_role_change, log_percentage_change
        member = self.get_member(member_id)
        old_role = member.role
        old_pct = member.default_percentage
        form = GroupMemberEditForm(request.POST, instance=member)
        if form.is_valid():
            updated = form.save()
            if updated.role != old_role:
                log_role_change(member, self.group_member, old_role, updated.role)
            if updated.default_percentage != old_pct:
                log_percentage_change(
                    member, self.group_member, old_pct, updated.default_percentage
                )
            messages.success(request, "Member updated.")
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group, "member": member,
        })


class GroupMemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, group_id, member_id):
        member = get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )
        from django.core.exceptions import ValidationError
        try:
            deactivate_member(member, self.group_member)
            messages.success(
                request,
                f"{member.user.get_full_name()} has been deactivated."
            )
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect("member_list", group_id=self.group.pk)


class GroupMemberRoleView(OwnerRequiredMixin, View):
    def post(self, request, group_id, member_id):
        from audit.services import log_role_change
        member = get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )
        new_role = request.POST.get("role")
        valid_roles = [GroupMember.Role.ADMIN, GroupMember.Role.MEMBER]
        if new_role not in valid_roles:
            messages.error(request, "Invalid role.")
            return redirect("member_list", group_id=self.group.pk)
        old_role = member.role
        member.role = new_role
        member.save()
        log_role_change(member, self.group_member, old_role, new_role)
        messages.success(request, f"Role updated to {new_role}.")
        return redirect("member_list", group_id=self.group.pk)


class RebalancePercentagesView(AdminRequiredMixin, View):
    template_name = "groups/rebalance.html"

    def get_active_members(self):
        return list(
            GroupMember.objects.filter(
                group=self.group,
                status=GroupMember.Status.ACTIVE,
            ).select_related("user")
        )

    def get(self, request, group_id):
        from django.shortcuts import render
        members = self.get_active_members()
        form = RebalanceForm(members=members)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        members = self.get_active_members()
        form = RebalanceForm(request.POST, members=members)
        if form.is_valid():
            percentages = {
                m.pk: form.cleaned_data[f"pct_{m.pk}"]
                for m in members
            }
            rebalance_percentages(self.group, percentages)
            messages.success(request, "Percentages updated.")
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })


class TransferOwnershipView(OwnerRequiredMixin, View):
    template_name = "groups/transfer_ownership.html"

    def get(self, request, group_id):
        from django.shortcuts import render
        form = TransferOwnershipForm(
            group=self.group,
            current_owner=self.group_member,
        )
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        form = TransferOwnershipForm(
            request.POST,
            group=self.group,
            current_owner=self.group_member,
        )
        if form.is_valid():
            transfer_ownership(
                self.group,
                self.group_member,
                form.cleaned_data["new_owner"],
            )
            messages.success(request, "Ownership transferred.")
            return redirect("group_detail", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })


class InvitationAcceptView(View):
    template_name = "groups/invitation_accept.html"

    def get(self, request, token):
        from django.shortcuts import render
        invitation = get_object_or_404(Invitation, token=token)
        return render(request, self.template_name, {
            "invitation": invitation,
        })

    def post(self, request, token):
        if not request.user.is_authenticated:
            from django.conf import settings as s
            return redirect(
                f"{s.LOGIN_URL}?next=/groups/invitations/{token}/"
            )
        from django.core.exceptions import ValidationError
        try:
            accept_invitation(str(token), request.user)
            messages.success(request, "You have joined the group.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect("group_list")


# =============================================================================
# ./groups/urls.py
# =============================================================================
from django.urls import path, include
from groups import views

group_detail_patterns = [
    path("", views.GroupDetailView.as_view(), name="group_detail"),
    path("edit/", views.GroupEditView.as_view(), name="group_edit"),
    path("archive/", views.GroupArchiveView.as_view(), name="group_archive"),
    path("transfer-ownership/", views.TransferOwnershipView.as_view(),
         name="group_transfer_ownership"),
    path("members/", views.GroupMemberListView.as_view(), name="member_list"),
    path("members/invite/", views.MemberInviteView.as_view(), name="member_invite"),
    path("members/rebalance/", views.RebalancePercentagesView.as_view(),
         name="member_rebalance"),
    path("members/<int:member_id>/edit/", views.GroupMemberEditView.as_view(),
         name="member_edit"),
    path("members/<int:member_id>/deactivate/",
         views.GroupMemberDeactivateView.as_view(), name="member_deactivate"),
    path("members/<int:member_id>/role/", views.GroupMemberRoleView.as_view(),
         name="member_role"),
    path("expenses/", include("expenses.urls")),
    path("payments/", include("payments.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit/", include("audit.urls")),
    path("reports/", include("reporting.urls")),
]

urlpatterns = [
    path("", views.GroupListView.as_view(), name="group_list"),
    path("create/", views.GroupCreateView.as_view(), name="group_create"),
    path("<int:group_id>/", include(group_detail_patterns)),
    path("invitations/<uuid:token>/", views.InvitationAcceptView.as_view(),
         name="invitation_accept"),
]


# =============================================================================
# ./groups/admin.py
# =============================================================================
from django.contrib import admin
from groups.models import Group, GroupMember, Invitation

admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(Invitation)


# =============================================================================
# ./expenses/models.py
# =============================================================================
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    paid_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="expenses_paid",
    )
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="expenses_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="expenses_deleted",
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.description} — {self.amount} ({self.group})"

    def clean(self):
        if self.paid_by.group != self.group:
            raise ValidationError(
                "The member who paid must belong to this group."
            )
        from groups.models import GroupMember
        if self.paid_by.status == GroupMember.Status.INACTIVE:
            raise ValidationError(
                "An inactive member cannot be recorded as having paid."
            )


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.PROTECT,
        related_name="splits",
    )
    group_member = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="expense_splits",
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Stored for auditability. Derived from expense.amount × percentage / 100.",
    )

    class Meta:
        unique_together = ("expense", "group_member")

    def __str__(self):
        return f"{self.group_member} owes {self.amount} for {self.expense}"


# =============================================================================
# ./expenses/services.py
# =============================================================================
from decimal import Decimal
from django.db import models as db_models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


def calculate_balance(group_member) -> Decimal:
    """
    Positive = member owes the pool.
    Negative = pool owes the member.
    """
    from expenses.models import ExpenseSplit
    from payments.models import Payment

    total_owed = (
        ExpenseSplit.objects
        .filter(
            group_member=group_member,
            expense__is_deleted=False,
        )
        .aggregate(total=db_models.Sum("amount"))["total"]
        or Decimal("0.00")
    )

    total_paid = (
        Payment.objects
        .filter(paid_by=group_member)
        .aggregate(total=db_models.Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return total_owed - total_paid


def calculate_group_balances(group) -> list:
    from groups.models import GroupMember
    memberships = (
        GroupMember.objects
        .filter(group=group)
        .select_related("user")
        .order_by("status", "user__first_name")
    )
    return [
        {
            "member": m,
            "balance": calculate_balance(m),
            "status": m.status,
            "role": m.role,
        }
        for m in memberships
    ]


@transaction.atomic
def create_expense(group, paid_by, created_by, form_data: dict, splits: list) -> "Expense":
    from expenses.models import Expense, ExpenseSplit

    total_pct = sum(s["percentage"] for s in splits)
    if round(total_pct, 2) != Decimal("100.00"):
        raise ValidationError("Splits must sum to 100.")

    expense = Expense.objects.create(
        group=group,
        paid_by=paid_by,
        created_by=created_by,
        **form_data,
    )

    for split in splits:
        ExpenseSplit.objects.create(
            expense=expense,
            group_member=split["group_member"],
            percentage=split["percentage"],
            amount=(expense.amount * split["percentage"] / Decimal("100.00")),
        )

    return expense


@transaction.atomic
def edit_expense(expense, form_data: dict, splits: list):
    for field, value in form_data.items():
        setattr(expense, field, value)
    expense.save()

    # Replace splits entirely
    expense.splits.all().delete()

    total_pct = sum(s["percentage"] for s in splits)
    if round(total_pct, 2) != Decimal("100.00"):
        raise ValidationError("Splits must sum to 100.")

    for split in splits:
        from expenses.models import ExpenseSplit
        ExpenseSplit.objects.create(
            expense=expense,
            group_member=split["group_member"],
            percentage=split["percentage"],
            amount=(expense.amount * split["percentage"] / Decimal("100.00")),
        )

    return expense


@transaction.atomic
def delete_expense(expense, deleted_by) -> None:
    from audit.services import log_expense_deletion
    expense.is_deleted = True
    expense.deleted_at = timezone.now()
    expense.deleted_by = deleted_by
    expense.save()
    log_expense_deletion(expense, deleted_by)


# =============================================================================
# ./expenses/forms.py
# =============================================================================
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


# =============================================================================
# ./expenses/urls.py
# =============================================================================
from django.urls import path
from expenses import views

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="expense_list"),
    path("add/", views.ExpenseCreateView.as_view(), name="expense_add"),
    path("<int:expense_id>/", views.ExpenseDetailView.as_view(),
         name="expense_detail"),
    path("<int:expense_id>/edit/", views.ExpenseEditView.as_view(),
         name="expense_edit"),
    path("<int:expense_id>/delete/", views.ExpenseDeleteView.as_view(),
         name="expense_delete"),
]


# =============================================================================
# ./expenses/admin.py
# =============================================================================
from django.contrib import admin
from expenses.models import Category, Expense, ExpenseSplit

admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(ExpenseSplit)


# =============================================================================
# ./payments/models.py
# =============================================================================
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class Payment(models.Model):
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    paid_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="payments_made",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.paid_by} paid {self.amount} into {self.group}"

    def clean(self):
        if self.paid_by.group != self.group:
            raise ValidationError(
                "The paying member must belong to this group."
            )


# =============================================================================
# ./payments/forms.py
# =============================================================================
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


# =============================================================================
# ./payments/views.py
# =============================================================================
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View
from payments.models import Payment
from payments.forms import PaymentForm
from groups.mixins import ActiveMemberRequiredMixin, AdminRequiredMixin


class PaymentListView(ActiveMemberRequiredMixin, ListView):
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
        form = PaymentForm()
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.group = self.group
            payment.paid_by = self.group_member
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


# =============================================================================
# ./payments/urls.py
# =============================================================================
from django.urls import path
from payments import views

urlpatterns = [
    path("", views.PaymentListView.as_view(), name="payment_list"),
    path("add/", views.PaymentCreateView.as_view(), name="payment_add"),
    path("<int:payment_id>/delete/", views.PaymentDeleteView.as_view(),
         name="payment_delete"),
]


# =============================================================================
# ./payments/admin.py
# =============================================================================
from django.contrib import admin
from payments.models import Payment

admin.site.register(Payment)


# =============================================================================
# ./notifications/models.py
# =============================================================================
from django.db import models


class Notification(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="notifications",
    )
    recipient = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        related_name="notifications_received",
    )
    message = models.TextField()
    balance_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The recipient's balance at the time this notification was generated.",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    triggered_by = models.ForeignKey(
        "groups.GroupMember",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notifications_triggered",
        help_text="Null if system-triggered.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification to {self.recipient} — {self.status}"


# =============================================================================
# ./notifications/services.py
# =============================================================================
from decimal import Decimal
from notifications.models import Notification
from groups.models import GroupMember


def generate_notifications(group, triggered_by=None) -> list:
    from expenses.services import calculate_group_balances
    balances = calculate_group_balances(group)
    notifications = []

    for entry in balances:
        member = entry["member"]
        balance = entry["balance"]

        if member.status != GroupMember.Status.ACTIVE:
            continue
        if balance == Decimal("0.00"):
            continue

        direction = "owe" if balance > 0 else "are owed"
        amount = abs(balance)

        notification = Notification.objects.create(
            group=group,
            recipient=member,
            message=(
                f"Hi {member.user.first_name}, "
                f"you currently {direction} {amount} "
                f"in {group.name}."
            ),
            balance_snapshot=balance,
            status=Notification.Status.PENDING,
            triggered_by=triggered_by,
        )
        notifications.append(notification)

    return notifications


# =============================================================================
# ./notifications/views.py
# =============================================================================
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, View
from notifications.models import Notification
from notifications.services import generate_notifications
from groups.mixins import AdminRequiredMixin


class NotificationListView(AdminRequiredMixin, ListView):
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 25

    def get_queryset(self):
        return Notification.objects.filter(
            group=self.group,
        ).select_related("recipient__user", "triggered_by__user")


class NotificationSendView(AdminRequiredMixin, View):
    def post(self, request, group_id):
        notifications = generate_notifications(
            self.group,
            triggered_by=self.group_member,
        )
        count = len(notifications)
        messages.success(
            request,
            f"{count} notification(s) queued for delivery."
        )
        return redirect("notification_list", group_id=self.group.pk)


# =============================================================================
# ./notifications/urls.py
# =============================================================================
from django.urls import path
from notifications import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("send/", views.NotificationSendView.as_view(), name="notification_send"),
]


# =============================================================================
# ./notifications/admin.py
# =============================================================================
from django.contrib import admin
from notifications.models import Notification

admin.site.register(Notification)


# =============================================================================
# ./reporting/views.py
# =============================================================================
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


# =============================================================================
# ./reporting/urls.py
# =============================================================================
from django.urls import path
from reporting import views

urlpatterns = [
    path("", views.ReportView.as_view(), name="report"),
]
