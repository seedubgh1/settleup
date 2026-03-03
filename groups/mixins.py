from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from groups.models import Group, GroupMember


class GroupContextMixin(LoginRequiredMixin):
    """
    Base mixin. Resolves the group from the URL and attaches
    self.group and self.group_member to the view.
    """
    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, pk=kwargs["group_id"])
        try:
            self.group_member = GroupMember.objects.get(
                group=self.group,
                user=request.user,
            )
        except GroupMember.DoesNotExist:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["group"] = self.group
        ctx["group_member"] = self.group_member
        return ctx


class GroupMemberRequiredMixin(GroupContextMixin):
    """Any member (active or inactive) of the group."""
    pass


class ActiveMemberRequiredMixin(GroupContextMixin):
    """Only active members."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.status != GroupMember.Status.ACTIVE:
            raise PermissionDenied
        return response


class AdminRequiredMixin(ActiveMemberRequiredMixin):
    """Active admins and owners only."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.role == GroupMember.Role.MEMBER:
            raise PermissionDenied
        return response


class OwnerRequiredMixin(ActiveMemberRequiredMixin):
    """Active owner only."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.group_member.role != GroupMember.Role.OWNER:
            raise PermissionDenied
        return response
