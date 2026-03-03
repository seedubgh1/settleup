from django.urls import path, include
from groups import views

group_detail_patterns = [
    path("", views.GroupDetailView.as_view(), name="group_detail"),
    path("edit/", views.GroupEditView.as_view(), name="group_edit"),
    path("archive/", views.GroupArchiveView.as_view(), name="group_archive"),
    path("transfer-ownership/", views.TransferOwnershipView.as_view(),
         name="group_transfer_ownership"),
    path("members/", views.GroupMemberListView.as_view(), name="member_list"),
    path("members/invite/", views.MemberInviteView.as_view(), name="member_invite"),
    path("members/rebalance/", views.RebalancePercentagesView.as_view(),
         name="member_rebalance"),
    path("members/<int:member_id>/edit/", views.GroupMemberEditView.as_view(),
         name="member_edit"),
    path("members/<int:member_id>/deactivate/",
         views.GroupMemberDeactivateView.as_view(), name="member_deactivate"),
    path("members/<int:member_id>/role/", views.GroupMemberRoleView.as_view(),
         name="member_role"),
    path("expenses/", include("expenses.urls")),
    path("payments/", include("payments.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit/", include("audit.urls")),
    path("reports/", include("reporting.urls")),
]

urlpatterns = [
    path("", views.GroupListView.as_view(), name="group_list"),
    path("create/", views.GroupCreateView.as_view(), name="group_create"),
    path("<int:group_id>/", include(group_detail_patterns)),
    path("invitations/<uuid:token>/", views.InvitationAcceptView.as_view(),
         name="invitation_accept"),
]
