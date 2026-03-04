from django.views.generic import ListView
from audit.models import AuditLog
from groups.mixins import ActiveMemberRequiredMixin, GroupMemberRequiredMixin


class AuditLogView(GroupMemberRequiredMixin, ListView):
    model = AuditLog
    template_name = "audit/audit_log.html"
    context_object_name = "audit_logs"
    paginate_by = 50

    def get_queryset(self):
        group = self.group  # set by mixin
        member = self.group_member  # set by mixin
        qs = AuditLog.objects.filter(
            group_member__group=group,
        ).select_related("group_member__user", "acted_by__user")

        # Regular members only see events that affected them
        from groups.models import GroupMember
        if member.role == GroupMember.Role.MEMBER:
            qs = qs.filter(group_member=member)

        return qs
