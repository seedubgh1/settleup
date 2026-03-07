import pytest
from decimal import Decimal
import factory
from factory.django import DjangoModelFactory

from users.models import User
from groups.models import Group, GroupMember
from expenses.models import Expense, ExpenseSplit, Category
from payments.models import Payment


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Sequence(lambda n: f"First{n}")
    last_name = factory.Sequence(lambda n: f"Last{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")
    created_by = factory.SubFactory(UserFactory)


class GroupMemberFactory(DjangoModelFactory):
    class Meta:
        model = GroupMember

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    role = GroupMember.Role.MEMBER
    default_percentage = Decimal("50.00")
    status = GroupMember.Status.ACTIVE


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class ExpenseFactory(DjangoModelFactory):
    class Meta:
        model = Expense

    group = factory.SubFactory(GroupFactory)
    paid_by = factory.SubFactory(GroupMemberFactory)
    created_by = factory.SubFactory(GroupMemberFactory)
    description = factory.Sequence(lambda n: f"Expense {n}")
    amount = Decimal("100.00")
    date = factory.django.mocked_now if False else factory.LazyFunction(
        lambda: __import__("datetime").date.today()
    )
    category = factory.SubFactory(CategoryFactory)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    group = factory.SubFactory(GroupFactory)
    paid_by = factory.SubFactory(GroupMemberFactory)
    amount = Decimal("50.00")
    date = factory.LazyFunction(lambda: __import__("datetime").date.today())


# ---------------------------------------------------------------------------
# Fixtures: a ready-made two-member group
# ---------------------------------------------------------------------------

@pytest.fixture
def two_member_group(db):
    """
    Returns a dict with:
      group, owner_user, owner_member, member_user, member_member, category
    Owner has 60%, member has 40%.
    """
    owner_user = UserFactory(username="owner", email="owner@example.com")
    member_user = UserFactory(username="member", email="member@example.com")

    group = GroupFactory(name="Test Group", created_by=owner_user)

    owner_member = GroupMemberFactory(
        user=owner_user,
        group=group,
        role=GroupMember.Role.OWNER,
        default_percentage=Decimal("60.00"),
    )
    member_member = GroupMemberFactory(
        user=member_user,
        group=group,
        role=GroupMember.Role.MEMBER,
        default_percentage=Decimal("40.00"),
    )

    category = CategoryFactory(name="Food")

    return {
        "group": group,
        "owner_user": owner_user,
        "owner_member": owner_member,
        "member_user": member_user,
        "member_member": member_member,
        "category": category,
    }
