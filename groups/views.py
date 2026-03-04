from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View
)
from groups.models import Group, GroupMember, Invitation
from groups.forms import (
    GroupForm, GroupMemberEditForm, RebalanceForm,
    InvitationForm, TransferOwnershipForm,
)
from groups.mixins import (
    ActiveMemberRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin,
    GroupMemberRequiredMixin,
)
from groups.services import (
    create_group, deactivate_member, transfer_ownership, accept_invitation,
    rebalance_percentages,
)
from expenses.services import calculate_group_balances
from django.utils import timezone
from django.conf import settings


class GroupListView(LoginRequiredMixin, ListView):
    template_name = "groups/group_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return GroupMember.objects.filter(
            user=self.request.user,
        ).select_related("group").order_by("-group__created_at")


class GroupCreateView(LoginRequiredMixin, CreateView):
    form_class = GroupForm
    template_name = "groups/group_form.html"

    def form_valid(self, form):
        group = create_group(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            created_by=self.request.user,
        )
        return redirect("group_detail", group_id=group.pk)


class GroupDetailView(GroupMemberRequiredMixin, DetailView):
    template_name = "groups/group_detail.html"

    def get_object(self):
        return self.group

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from expenses.services import calculate_balance
        from expenses.models import Expense
        ctx["my_balance"] = calculate_balance(self.group_member)
        ctx["recent_expenses"] = (
            Expense.objects
            .filter(group=self.group, is_deleted=False)
            .select_related("paid_by__user", "category")
            .order_by("-date")[:10]
        )
        return ctx


class GroupEditView(OwnerRequiredMixin, UpdateView):
    form_class = GroupForm
    template_name = "groups/group_form.html"

    def get_object(self):
        return self.group

    def get_success_url(self):
        return reverse("group_detail", kwargs={"group_id": self.group.pk})


class GroupArchiveView(OwnerRequiredMixin, View):
    def post(self, request, group_id):
        self.group.is_active = False
        self.group.save()
        messages.success(request, f"{self.group.name} has been archived.")
        return redirect("group_list")


class GroupMemberListView(GroupMemberRequiredMixin, ListView):
    template_name = "groups/member_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return GroupMember.objects.filter(
            group=self.group,
        ).select_related("user").order_by("status", "user__first_name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["balances"] = calculate_group_balances(self.group)
        return ctx


class MemberInviteView(AdminRequiredMixin, View):
    template_name = "groups/member_invite.html"

    def get_form(self):
        return InvitationForm(
            self.request.POST or None,
            group=self.group,
        )

    def get(self, request, group_id):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": self.get_form(),
            "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        form = self.get_form()
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.group = self.group
            invitation.invited_by = self.group_member
            invitation.expires_at = timezone.now() + timezone.timedelta(
                days=settings.INVITATION_EXPIRY_DAYS
            )
            invitation.save()
            messages.success(
                request,
                f"Invitation recorded for {invitation.email}."
            )
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form,
            "group": self.group,
        })


class GroupMemberEditView(AdminRequiredMixin, View):
    template_name = "groups/member_form.html"

    def get_member(self, member_id):
        return get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )

    def get(self, request, group_id, member_id):
        from django.shortcuts import render
        member = self.get_member(member_id)
        form = GroupMemberEditForm(instance=member)
        return render(request, self.template_name, {
            "form": form, "group": self.group, "member": member,
        })

    def post(self, request, group_id, member_id):
        from django.shortcuts import render
        from audit.services import log_role_change, log_percentage_change
        member = self.get_member(member_id)
        old_role = member.role
        old_pct = member.default_percentage
        form = GroupMemberEditForm(request.POST, instance=member)
        if form.is_valid():
            updated = form.save()
            if updated.role != old_role:
                log_role_change(member, self.group_member, old_role, updated.role)
            if updated.default_percentage != old_pct:
                log_percentage_change(
                    member, self.group_member, old_pct, updated.default_percentage
                )
            messages.success(request, "Member updated.")
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group, "member": member,
        })


class GroupMemberDeactivateView(AdminRequiredMixin, View):
    def post(self, request, group_id, member_id):
        member = get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )
        from django.core.exceptions import ValidationError
        try:
            deactivate_member(member, self.group_member)
            messages.success(
                request,
                f"{member.user.get_full_name()} has been deactivated."
            )
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect("member_list", group_id=self.group.pk)


class GroupMemberRoleView(OwnerRequiredMixin, View):
    def post(self, request, group_id, member_id):
        from audit.services import log_role_change
        member = get_object_or_404(
            GroupMember, pk=member_id, group=self.group
        )
        new_role = request.POST.get("role")
        valid_roles = [GroupMember.Role.ADMIN, GroupMember.Role.MEMBER]
        if new_role not in valid_roles:
            messages.error(request, "Invalid role.")
            return redirect("member_list", group_id=self.group.pk)
        old_role = member.role
        member.role = new_role
        member.save()
        log_role_change(member, self.group_member, old_role, new_role)
        messages.success(request, f"Role updated to {new_role}.")
        return redirect("member_list", group_id=self.group.pk)


class RebalancePercentagesView(AdminRequiredMixin, View):
    template_name = "groups/rebalance.html"

    def get_active_members(self):
        return list(
            GroupMember.objects.filter(
                group=self.group,
                status=GroupMember.Status.ACTIVE,
            ).select_related("user")
        )

    def get(self, request, group_id):
        from django.shortcuts import render
        members = self.get_active_members()
        form = RebalanceForm(members=members)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        members = self.get_active_members()
        form = RebalanceForm(request.POST, members=members)
        if form.is_valid():
            percentages = {
                m.pk: form.cleaned_data[f"pct_{m.pk}"]
                for m in members
            }
            rebalance_percentages(self.group, percentages, acted_by=self.group_member)
            messages.success(request, "Percentages updated.")
            return redirect("member_list", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })


class TransferOwnershipView(OwnerRequiredMixin, View):
    template_name = "groups/transfer_ownership.html"

    def get(self, request, group_id):
        from django.shortcuts import render
        form = TransferOwnershipForm(
            group=self.group,
            current_owner=self.group_member,
        )
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })

    def post(self, request, group_id):
        from django.shortcuts import render
        form = TransferOwnershipForm(
            request.POST,
            group=self.group,
            current_owner=self.group_member,
        )
        if form.is_valid():
            transfer_ownership(
                self.group,
                self.group_member,
                form.cleaned_data["new_owner"],
            )
            messages.success(request, "Ownership transferred.")
            return redirect("group_detail", group_id=self.group.pk)
        return render(request, self.template_name, {
            "form": form, "group": self.group,
        })


class InvitationAcceptView(View):
    template_name = "groups/invitation_accept.html"

    def get(self, request, token):
        from django.shortcuts import render
        invitation = get_object_or_404(Invitation, token=token)
        return render(request, self.template_name, {
            "invitation": invitation,
        })

    def post(self, request, token):
        if not request.user.is_authenticated:
            from django.conf import settings as s
            return redirect(
                f"{s.LOGIN_URL}?next=/groups/invitations/{token}/"
            )
        from django.core.exceptions import ValidationError
        try:
            accept_invitation(str(token), request.user)
            messages.success(request, "You have joined the group.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect("group_list")
