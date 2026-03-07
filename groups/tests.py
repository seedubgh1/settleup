import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from groups.models import Group, GroupMember
from groups.services import (
    create_group,
    rebalance_percentages,
    deactivate_member,
    transfer_ownership,
)
from conftest import UserFactory, GroupFactory, GroupMemberFactory


@pytest.mark.django_db
class TestCreateGroup:
    def test_creates_group_with_owner(self):
        user = UserFactory()
        group = create_group("My Group", "desc", created_by=user)
        assert group.pk is not None
        membership = GroupMember.objects.get(group=group, user=user)
        assert membership.role == GroupMember.Role.OWNER
        assert membership.default_percentage == Decimal("100.00")

    def test_owner_is_sole_active_member_at_100_pct(self):
        user = UserFactory()
        group = create_group("Solo", "", created_by=user)
        members = GroupMember.objects.filter(group=group, status=GroupMember.Status.ACTIVE)
        assert members.count() == 1
        assert members.first().default_percentage == Decimal("100.00")


@pytest.mark.django_db
class TestRebalancePercentages:
    def test_rebalance_updates_percentages(self, two_member_group):
        g = two_member_group
        new_pcts = {
            g["owner_member"].pk: Decimal("70.00"),
            g["member_member"].pk: Decimal("30.00"),
        }
        rebalance_percentages(g["group"], new_pcts, acted_by=g["owner_member"])
        g["owner_member"].refresh_from_db()
        g["member_member"].refresh_from_db()
        assert g["owner_member"].default_percentage == Decimal("70.00")
        assert g["member_member"].default_percentage == Decimal("30.00")

    def test_rebalance_not_100_raises(self, two_member_group):
        g = two_member_group
        bad_pcts = {
            g["owner_member"].pk: Decimal("60.00"),
            g["member_member"].pk: Decimal("20.00"),
        }
        with pytest.raises(ValidationError, match="100"):
            rebalance_percentages(g["group"], bad_pcts)


@pytest.mark.django_db
class TestDeactivateMember:
    def test_deactivates_member_with_zero_balance(self, two_member_group):
        g = two_member_group
        deactivate_member(g["member_member"], g["owner_member"])
        g["member_member"].refresh_from_db()
        assert g["member_member"].status == GroupMember.Status.INACTIVE
        assert g["member_member"].deactivated_at is not None

    def test_auto_rebalances_remaining_members(self, two_member_group):
        g = two_member_group
        deactivate_member(g["member_member"], g["owner_member"])
        g["owner_member"].refresh_from_db()
        assert g["owner_member"].default_percentage == Decimal("100.00")

    def test_cannot_deactivate_owner(self, two_member_group):
        g = two_member_group
        with pytest.raises(ValidationError, match="owner"):
            deactivate_member(g["owner_member"], g["owner_member"])

    def test_member_cannot_deactivate_others(self, two_member_group):
        from conftest import GroupMemberFactory
        g = two_member_group
        # Add a third member so member_member can try to deactivate them
        third_member = GroupMemberFactory(
            group=g["group"],
            role=GroupMember.Role.MEMBER,
            default_percentage=Decimal("0.00"),
        )
        with pytest.raises(ValidationError, match="Members cannot"):
            deactivate_member(third_member, g["member_member"])

    def test_cannot_deactivate_with_outstanding_balance(self, two_member_group):
        from expenses.services import create_expense
        import datetime
        g = two_member_group
        # Create an expense so member_member has a non-zero balance
        create_expense(
            group=g["group"],
            paid_by=g["owner_member"],
            created_by=g["owner_member"],
            form_data={
                "description": "Lunch",
                "amount": Decimal("100.00"),
                "date": datetime.date.today(),
                "category": g["category"],
            },
            splits=[
                {"group_member": g["owner_member"], "percentage": Decimal("60.00")},
                {"group_member": g["member_member"], "percentage": Decimal("40.00")},
            ],
        )
        with pytest.raises(ValidationError, match="outstanding balance"):
            deactivate_member(g["member_member"], g["owner_member"])


@pytest.mark.django_db
class TestTransferOwnership:
    def test_transfers_owner_role(self, two_member_group):
        g = two_member_group
        transfer_ownership(g["group"], g["owner_member"], g["member_member"])
        g["owner_member"].refresh_from_db()
        g["member_member"].refresh_from_db()
        assert g["member_member"].role == GroupMember.Role.OWNER
        assert g["owner_member"].role == GroupMember.Role.ADMIN
