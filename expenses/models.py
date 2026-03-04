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

    # def clean(self):
    #     if self.paid_by.group != self.group:
    #         raise ValidationError(
    #             "The member who paid must belong to this group."
    #         )
    #     from groups.models import GroupMember
    #     if self.paid_by.status == GroupMember.Status.INACTIVE:
    #         raise ValidationError(
    #             "An inactive member cannot be recorded as having paid."
    #         )


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
