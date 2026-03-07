"""
Integration tests — full request/response cycle using Django's test client.
Covers: register, login, create group, add expense, record payment.
"""
import datetime
import pytest
from decimal import Decimal
from django.urls import reverse

from conftest import UserFactory, GroupMemberFactory, CategoryFactory
from groups.models import Group, GroupMember
from expenses.models import Expense
from payments.models import Payment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _formset_data(members, prefix="form"):
    """Build management form + split rows for ExpenseSplitFormSet."""
    data = {
        f"{prefix}-TOTAL_FORMS": str(len(members)),
        f"{prefix}-INITIAL_FORMS": str(len(members)),
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }
    for i, (member, pct) in enumerate(members):
        data[f"{prefix}-{i}-group_member_id"] = str(member.pk)
        data[f"{prefix}-{i}-member_name"] = member.user.get_full_name()
        data[f"{prefix}-{i}-percentage"] = str(pct)
        data[f"{prefix}-{i}-include"] = "on"
    return data


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegister:
    def test_register_creates_user_and_logs_in(self, client):
        url = reverse("register")
        response = client.post(url, {
            "username": "newuser",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password1": "str0ng!pass",
            "password2": "str0ng!pass",
        })
        assert response.status_code == 302
        assert response["Location"] == reverse("group_list")
        # User is now authenticated
        response2 = client.get(reverse("group_list"))
        assert response2.status_code == 200

    def test_register_duplicate_email_fails(self, client):
        UserFactory(email="taken@example.com")
        url = reverse("register")
        response = client.post(url, {
            "username": "newuser2",
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "taken@example.com",
            "password1": "str0ng!pass",
            "password2": "str0ng!pass",
        })
        assert response.status_code == 200  # re-renders form with errors

    def test_register_missing_first_name_fails(self, client):
        url = reverse("register")
        response = client.post(url, {
            "username": "newuser3",
            "first_name": "",
            "last_name": "Jones",
            "email": "bob@example.com",
            "password1": "str0ng!pass",
            "password2": "str0ng!pass",
        })
        assert response.status_code == 200  # form invalid, re-rendered


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLogin:
    def test_login_with_valid_credentials(self, client):
        user = UserFactory(username="loginuser")
        user.set_password("testpass123")
        user.save()
        response = client.post(reverse("login"), {
            "username": "loginuser",
            "password": "testpass123",
        })
        assert response.status_code == 302

    def test_login_with_wrong_password(self, client):
        user = UserFactory(username="loginuser2")
        user.set_password("correctpass")
        user.save()
        response = client.post(reverse("login"), {
            "username": "loginuser2",
            "password": "wrongpass",
        })
        assert response.status_code == 200  # re-renders form

    def test_unauthenticated_redirects_to_login(self, client):
        response = client.get(reverse("group_list"))
        assert response.status_code == 302
        assert "login" in response["Location"]


# ---------------------------------------------------------------------------
# Create Group
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCreateGroup:
    def test_create_group_success(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.post(reverse("group_create"), {
            "name": "Weekend Trip",
            "description": "Expenses for the trip",
        })
        assert response.status_code == 302
        group = Group.objects.get(name="Weekend Trip")
        assert GroupMember.objects.filter(
            group=group,
            user=user,
            role=GroupMember.Role.OWNER,
        ).exists()

    def test_create_group_requires_login(self, client):
        response = client.post(reverse("group_create"), {"name": "Test"})
        assert response.status_code == 302
        assert "login" in response["Location"]

    def test_create_group_empty_name_fails(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.post(reverse("group_create"), {"name": "", "description": ""})
        assert response.status_code == 200  # form invalid


# ---------------------------------------------------------------------------
# Add Expense
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAddExpense:
    def test_add_expense_success(self, client, two_member_group):
        g = two_member_group
        client.force_login(g["owner_user"])
        url = reverse("expense_add", kwargs={"group_id": g["group"].pk})

        post_data = {
            "description": "Dinner",
            "amount": "100.00",
            "category": g["category"].pk,
            "date": str(datetime.date.today()),
            "notes": "",
        }
        post_data.update(_formset_data([
            (g["owner_member"], "60.00"),
            (g["member_member"], "40.00"),
        ]))

        response = client.post(url, post_data)
        assert response.status_code == 302
        assert Expense.objects.filter(
            group=g["group"], description="Dinner"
        ).exists()

    def test_add_expense_splits_not_100_fails(self, client, two_member_group):
        g = two_member_group
        client.force_login(g["owner_user"])
        url = reverse("expense_add", kwargs={"group_id": g["group"].pk})

        post_data = {
            "description": "Bad Split",
            "amount": "100.00",
            "category": g["category"].pk,
            "date": str(datetime.date.today()),
            "notes": "",
        }
        post_data.update(_formset_data([
            (g["owner_member"], "60.00"),
            (g["member_member"], "30.00"),  # only 90%, should fail
        ]))

        response = client.post(url, post_data)
        assert response.status_code == 200  # form re-rendered with errors
        assert not Expense.objects.filter(description="Bad Split").exists()

    def test_add_expense_requires_active_member(self, client, two_member_group):
        g = two_member_group
        g["member_member"].status = GroupMember.Status.INACTIVE
        g["member_member"].save()
        client.force_login(g["member_user"])
        url = reverse("expense_add", kwargs={"group_id": g["group"].pk})
        response = client.get(url)
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Record Payment
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRecordPayment:
    def test_record_payment_success(self, client, two_member_group):
        g = two_member_group
        client.force_login(g["member_user"])
        url = reverse("payment_add", kwargs={"group_id": g["group"].pk})

        response = client.post(url, {
            "amount": "40.00",
            "date": str(datetime.date.today()),
            "notes": "",
        })
        assert response.status_code == 302
        assert Payment.objects.filter(
            group=g["group"],
            paid_by=g["member_member"],
            amount=Decimal("40.00"),
        ).exists()

    def test_record_payment_invalid_amount_fails(self, client, two_member_group):
        g = two_member_group
        client.force_login(g["member_user"])
        url = reverse("payment_add", kwargs={"group_id": g["group"].pk})
        response = client.post(url, {
            "amount": "-10.00",
            "date": str(datetime.date.today()),
            "notes": "",
        })
        assert response.status_code == 200  # form re-rendered

    def test_record_payment_requires_active_member(self, client, two_member_group):
        g = two_member_group
        g["member_member"].status = GroupMember.Status.INACTIVE
        g["member_member"].save()
        client.force_login(g["member_user"])
        url = reverse("payment_add", kwargs={"group_id": g["group"].pk})
        response = client.get(url)
        assert response.status_code == 403
