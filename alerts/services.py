from decimal import Decimal
from django.utils import timezone
from alerts.models import Alert


def alert_percentage_change(
    recipient,
    old_percentage: Decimal,
    new_percentage: Decimal,
    reason: str,
) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.PERCENTAGE_CHANGED,
        message=(
            f"Your default contribution percentage in {recipient.group.name} "
            f"has changed from {old_percentage}% to {new_percentage}%. "
            f"Reason: {reason}"
        ),
    )


def alert_member_deactivated(recipient, deactivated_member) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.MEMBER_DEACTIVATED,
        message=(
            f"{deactivated_member.user.get_full_name()} has been removed "
            f"from {recipient.group.name}."
        ),
    )


def alert_ownership_transferred(recipient, old_owner, new_owner) -> Alert:
    return Alert.objects.create(
        recipient=recipient,
        alert_type=Alert.AlertType.OWNERSHIP_TRANSFERRED,
        message=(
            f"Ownership of {recipient.group.name} has been transferred "
            f"from {old_owner.user.get_full_name()} "
            f"to {new_owner.user.get_full_name()}."
        ),
    )


def mark_alert_read(alert: Alert) -> None:
    alert.is_read = True
    alert.read_at = timezone.now()
    alert.save()


def get_unread_alerts(group_member):
    return Alert.objects.filter(
        recipient=group_member,
        is_read=False,
    )
