from decimal import Decimal
from django.db import models as db_models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from groups.models import GroupMember
from expenses.models import Expense, ExpenseSplit


def calculate_balance(group_member) -> Decimal:
    """
    Positive = member owes the pool.
    Negative = pool owes the member.
    """
    # from expenses.models import ExpenseSplit
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
    # from groups.models import GroupMember # moved to top of this file
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
    # from expenses.models import Expense, ExpenseSplit

    # Validate paid_by here instead of on the model
    if paid_by.group != group:
        raise ValidationError("The member who paid must belong to this group.")
    if paid_by.status == GroupMember.Status.INACTIVE:
        raise ValidationError("An inactive member cannot be recorded as having paid.")

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
