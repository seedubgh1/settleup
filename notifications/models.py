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
