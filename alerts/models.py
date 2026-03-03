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
