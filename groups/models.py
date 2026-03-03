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
