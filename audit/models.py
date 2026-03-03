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
