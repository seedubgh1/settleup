from audit.models import AuditLog


def log_role_change(group_member, acted_by, old_role: str, new_role: str) -> AuditLog:
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.ROLE_CHANGED,
        old_value=old_role,
        new_value=new_role,
    )


def log_percentage_change(
    group_member, acted_by, old_percentage, new_percentage
) -> AuditLog:
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.PERCENTAGE_CHANGED,
        old_value=str(old_percentage),
        new_value=str(new_percentage),
    )


def log_member_deactivation(group_member, acted_by) -> AuditLog:
    from groups.models import GroupMember
    return AuditLog.objects.create(
        group_member=group_member,
        acted_by=acted_by,
        event_type=AuditLog.EventType.MEMBER_DEACTIVATED,
        old_value=GroupMember.Status.ACTIVE,
        new_value=GroupMember.Status.INACTIVE,
    )


def log_ownership_transfer(old_owner, new_owner) -> AuditLog:
    return AuditLog.objects.create(
        group_member=new_owner,
        acted_by=old_owner,
        event_type=AuditLog.EventType.OWNERSHIP_TRANSFERRED,
        old_value=old_owner.user.get_full_name(),
        new_value=new_owner.user.get_full_name(),
    )


def log_expense_deletion(expense, deleted_by) -> AuditLog:
    return AuditLog.objects.create(
        group_member=deleted_by,
        acted_by=deleted_by,
        event_type=AuditLog.EventType.EXPENSE_DELETED,
        old_value=str(expense.pk),
        new_value=expense.description,
    )
