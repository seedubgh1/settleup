from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from groups.models import Group, GroupMember, Invitation


@transaction.atomic
def create_group(name: str, description: str, created_by) -> Group:
    """
    Creates a group and assigns the creator as owner with 100% default
    percentage. 100% because they are the sole active member.
    """
    group = Group.objects.create(
        name=name,
        description=description,
        created_by=created_by,
    )
    GroupMember.objects.create(
        user=created_by,
        group=group,
        role=GroupMember.Role.OWNER,
        default_percentage=Decimal("100.00"),
    )
    return group


@transaction.atomic
def rebalance_percentages(group: Group, percentages: dict, acted_by=None) -> None:
    """
    Updates default percentages for active members.
    percentages: {group_member_pk: Decimal}
    Validates sum equals 100 before writing.
    """
    from audit.services import log_percentage_change
    from alerts.services import alert_percentage_change

    total = sum(percentages.values())
    if round(total, 2) != Decimal("100.00"):
        raise ValidationError(
            f"Percentages must sum to 100. Got {total}."
        )

    for pk, new_pct in percentages.items():
        member = GroupMember.objects.get(pk=pk)
        old_pct = member.default_percentage

        member.default_percentage = new_pct
        member.save()

        if old_pct != new_pct and acted_by:
            log_percentage_change(member, acted_by, old_pct, new_pct)
            alert_percentage_change(
                recipient=member,
                old_percentage=old_pct,
                new_percentage=new_pct,
                reason="Contribution percentages were manually rebalanced",
            )


@transaction.atomic
def deactivate_member(member: GroupMember, acting_member: GroupMember) -> None:
    """
    Deactivates a member after validating preconditions,
    then auto-rebalances remaining active members.
    Logs the deactivation and percentage changes to the audit log.
    """
    from expenses.services import calculate_balance
    from audit.services import log_member_deactivation
    from alerts.services import alert_member_deactivated

    if member.role == GroupMember.Role.OWNER:
        raise ValidationError("Cannot deactivate the group owner.")

    if acting_member.role == GroupMember.Role.MEMBER:
        raise ValidationError("Members cannot deactivate other members.")

    if (
        acting_member.role == GroupMember.Role.ADMIN
        and member.role == GroupMember.Role.ADMIN
    ):
        raise ValidationError("Admins cannot deactivate other admins.")

    balance = calculate_balance(member)
    if balance != Decimal("0.00"):
        raise ValidationError(
            f"Cannot deactivate {member.user.get_full_name()} — "
            f"outstanding balance of {balance}."
        )

    member.status = GroupMember.Status.INACTIVE
    member.deactivated_at = timezone.now()
    member.save()

    log_member_deactivation(member, acting_member)

    # Notify remaining active members
    active_members = GroupMember.objects.filter(
        group=member.group,
        status=GroupMember.Status.ACTIVE,
    )
    for m in active_members:
        alert_member_deactivated(m, member)

    _auto_rebalance_after_deactivation(member.group, member, acting_member)


def _auto_rebalance_after_deactivation(
    group: Group,
    deactivated_member: GroupMember,
    acted_by: GroupMember,
) -> None:
    """
    Redistributes the deactivated member's percentage proportionally
    across remaining active members.
    """
    from audit.services import log_percentage_change
    from alerts.services import alert_percentage_change

    active_members = list(
        GroupMember.objects.filter(
            group=group,
            status=GroupMember.Status.ACTIVE,
        )
    )

    if not active_members:
        return

    old_percentages = {m.pk: m.default_percentage for m in active_members}
    remaining_total = sum(m.default_percentage for m in active_members)

    if remaining_total == 0:
        even_share = Decimal("100.00") / len(active_members)
        new_percentages = {m.pk: round(even_share, 2) for m in active_members}
    else:
        new_percentages = {
            m.pk: round(
                (m.default_percentage / remaining_total) * Decimal("100.00"), 2
            )
            for m in active_members
        }

    # Correct rounding drift — assign remainder to largest-share member
    total_assigned = sum(new_percentages.values())
    drift = round(Decimal("100.00") - total_assigned, 2)
    if drift != 0:
        largest_pk = max(new_percentages, key=new_percentages.get)
        new_percentages[largest_pk] += drift

    reason = (
        f"{deactivated_member.user.get_full_name()} was removed from the group"
    )

    for m in active_members:
        old_pct = old_percentages[m.pk]
        new_pct = new_percentages[m.pk]
        m.default_percentage = new_pct
        m.save()

        if old_pct != new_pct:
            log_percentage_change(m, acted_by, old_pct, new_pct)
            alert_percentage_change(m, old_pct, new_pct, reason)


@transaction.atomic
def transfer_ownership(
    group: Group,
    current_owner: GroupMember,
    new_owner_member: GroupMember,
) -> None:
    from audit.services import log_ownership_transfer, log_role_change
    from alerts.services import alert_ownership_transferred

    new_owner_member.role = GroupMember.Role.OWNER
    new_owner_member.save()

    current_owner.role = GroupMember.Role.ADMIN
    current_owner.save()

    log_ownership_transfer(current_owner, new_owner_member)
    log_role_change(
        current_owner, current_owner,
        GroupMember.Role.OWNER, GroupMember.Role.ADMIN,
    )

    # Alert all active members
    active_members = GroupMember.objects.filter(
        group=group,
        status=GroupMember.Status.ACTIVE,
    )
    for m in active_members:
        alert_ownership_transferred(m, current_owner, new_owner_member)


@transaction.atomic
def accept_invitation(token: str, user) -> GroupMember:
    """
    Accepts an invitation and creates a GroupMember record.
    """
    from django.core.exceptions import ValidationError

    try:
        invitation = Invitation.objects.select_for_update().get(token=token)
    except Invitation.DoesNotExist:
        raise ValidationError("Invalid invitation link.")

    if invitation.status != Invitation.Status.PENDING:
        raise ValidationError(
            f"This invitation has already been {invitation.status}."
        )

    import django.utils.timezone as tz
    if tz.now() > invitation.expires_at:
        invitation.status = Invitation.Status.EXPIRED
        invitation.save()
        raise ValidationError("This invitation has expired.")

    member = GroupMember.objects.create(
        user=user,
        group=invitation.group,
        role=GroupMember.Role.MEMBER,
        default_percentage=invitation.default_percentage,
    )

    invitation.status = Invitation.Status.ACCEPTED
    invitation.accepted_at = tz.now()
    invitation.save()

    return member
