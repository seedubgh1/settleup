import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from expenses.services import (
    calculate_balance,
    calculate_group_balances,
    create_expense,
    edit_expense,
    delete_expense,
)
from conftest import PaymentFactory, ExpenseFactory


@pytest.mark.django_db
class TestCalculateBalance:
    def test_zero_with_no_activity(self, two_member_group):
        owner = two_member_group["owner_member"]
        assert calculate_balance(owner) == Decimal("0.00")

    def test_balance_equals_split_amount(self, two_member_group):
        g = two_member_group
        splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("40.00")},
        ]
        create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data={
                "description": "Dinner",
                "amount": Decimal("100.00"),
                "date": __import__("datetime").date.today(),
                "category": g["category"],
            },
            splits=splits,
        )
        # owner paid $100, split is $60 → net = 60 - 100 = -40 (owed to owner)
        assert calculate_balance(g["owner_member"]) == Decimal("-40.00")
        # member paid nothing, split is $40 → net = 40
        assert calculate_balance(g["member_member"]) == Decimal("40.00")

    def test_payment_reduces_balance(self, two_member_group):
        g = two_member_group
        splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("40.00")},
        ]
        create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data={
                "description": "Groceries",
                "amount": Decimal("100.00"),
                "date": __import__("datetime").date.today(),
                "category": g["category"],
            },
            splits=splits,
        )
        PaymentFactory(group=g["group"], paid_by=g["member_member"], amount=Decimal("40.00"))
        assert calculate_balance(g["member_member"]) == Decimal("0.00")
        # owner's balance: split $60 - paid expense $100 = -40, unaffected by member's payment
        assert calculate_balance(g["owner_member"]) == Decimal("-40.00")

    def test_deleted_expense_excluded(self, two_member_group):
        g = two_member_group
        splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("40.00")},
        ]
        expense = create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data={
                "description": "Deleted",
                "amount": Decimal("100.00"),
                "date": __import__("datetime").date.today(),
                "category": g["category"],
            },
            splits=splits,
        )
        delete_expense(expense, g["owner_member"])
        assert calculate_balance(g["member_member"]) == Decimal("0.00")


@pytest.mark.django_db
class TestCreateExpense:
    def _splits(self, g):
        return [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("40.00")},
        ]

    def _form_data(self, g, amount="100.00", description="Test"):
        return {
            "description": description,
            "amount": Decimal(amount),
            "date": __import__("datetime").date.today(),
            "category": g["category"],
        }

    def test_creates_expense_and_splits(self, two_member_group):
        g = two_member_group
        expense = create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data=self._form_data(g),
            splits=self._splits(g),
        )
        assert expense.pk is not None
        assert expense.splits.count() == 2

    def test_split_amounts_correct(self, two_member_group):
        g = two_member_group
        expense = create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data=self._form_data(g, amount="200.00"),
            splits=self._splits(g),
        )
        amounts = {s.group_member_id: s.amount for s in expense.splits.all()}
        assert amounts[g["owner_member"].pk] == Decimal("120.00")
        assert amounts[g["member_member"].pk] == Decimal("80.00")

    def test_splits_not_100_raises(self, two_member_group):
        g = two_member_group
        bad_splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("30.00")},
        ]
        with pytest.raises(ValidationError, match="100"):
            create_expense(
                group=g["group"],
                paid_by=g["owner_member"],
                created_by=g["owner_member"],
                form_data=self._form_data(g),
                splits=bad_splits,
            )

    def test_paid_by_wrong_group_raises(self, two_member_group):
        from conftest import GroupMemberFactory
        g = two_member_group
        other_member = GroupMemberFactory()  # belongs to a different group
        with pytest.raises(ValidationError):
            create_expense(
                group=g["group"],
                paid_by=other_member,
                created_by=g["owner_member"],
                form_data=self._form_data(g),
                splits=self._splits(g),
            )

    def test_inactive_paid_by_raises(self, two_member_group):
        from groups.models import GroupMember
        g = two_member_group
        g["member_member"].status = GroupMember.Status.INACTIVE
        g["member_member"].save()
        with pytest.raises(ValidationError, match="inactive"):
            create_expense(
                group=g["group"],
                paid_by=g["member_member"],
                created_by=g["owner_member"],
                form_data=self._form_data(g),
                splits=self._splits(g),
            )


@pytest.mark.django_db
class TestEditExpense:
    def test_edit_updates_amount_and_splits(self, two_member_group):
        g = two_member_group
        splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
            {"group_member": g["member_member"], "percentage": Decimal("40.00")},
        ]
        expense = create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data={
                "description": "Original",
                "amount": Decimal("100.00"),
                "date": __import__("datetime").date.today(),
                "category": g["category"],
            },
            splits=splits,
        )
        new_splits = [
            {"group_member": g["owner_member"], "percentage": Decimal("50.00")},
            {"group_member": g["member_member"], "percentage": Decimal("50.00")},
        ]
        edit_expense(
            expense,
            form_data={"amount": Decimal("200.00"), "description": "Edited"},
            splits=new_splits,
        )
        expense.refresh_from_db()
        assert expense.amount == Decimal("200.00")
        assert expense.description == "Edited"
        amounts = {s.group_member_id: s.amount for s in expense.splits.all()}
        assert amounts[g["owner_member"].pk] == Decimal("100.00")
        assert amounts[g["member_member"].pk] == Decimal("100.00")


@pytest.mark.django_db
class TestDeleteExpense:
    def test_soft_delete_sets_flag(self, two_member_group):
        g = two_member_group
        expense = ExpenseFactory(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            category=g["category"],
        )
        delete_expense(expense, g["owner_member"])
        expense.refresh_from_db()
        assert expense.is_deleted is True
        assert expense.deleted_at is not None


@pytest.mark.django_db
class TestCalculateGroupBalances:
    def test_returns_entry_per_member(self, two_member_group):
        g = two_member_group
        balances = calculate_group_balances(g["group"])
        assert len(balances) == 2
        member_pks = {e["member"].pk for e in balances}
        assert g["owner_member"].pk in member_pks
        assert g["member_member"].pk in member_pks
