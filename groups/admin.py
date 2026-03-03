from django.contrib import admin
from groups.models import Group, GroupMember, Invitation

admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(Invitation)
