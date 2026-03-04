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

    # def clean(self):
    #     if self.paid_by.group != self.group:
    #         raise ValidationError(
    #             "The paying member must belong to this group."
    #         )
