from decimal import Decimal
from notifications.models import Notification
from groups.models import GroupMember


def generate_notifications(group, triggered_by=None) -> list:
    from expenses.services import calculate_group_balances
    balances = calculate_group_balances(group)
    notifications = []

    for entry in balances:
        member = entry["member"]
        balance = entry["balance"]

        if member.status != GroupMember.Status.ACTIVE:
            continue
        if balance == Decimal("0.00"):
            continue

        direction = "owe" if balance > 0 else "are owed"
        amount = abs(balance)

        notification = Notification.objects.create(
            group=group,
            recipient=member,
            message=(
                f"Hi {member.user.first_name}, "
                f"you currently {direction} {amount} "
                f"in {group.name}."
            ),
            balance_snapshot=balance,
            status=Notification.Status.PENDING,
            triggered_by=triggered_by,
        )
        notifications.append(notification)

    return notifications
