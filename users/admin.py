from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'firstName', 'lastName', 'role', 'is_staff', 'is_superuser']
    list_filter = ['role', 'is_staff', 'is_superuser']
    search_fields = ['email', 'firstName', 'lastName']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['get_first_name', 'get_last_name', 'age', 'sex']
    list_filter = ['sex']
    search_fields = ['user__firstName', 'user__lastName']

    def get_first_name(self, obj):
        return obj.user.firstName
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.lastName
    get_last_name.short_description = 'Last Name'

class RoleChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'requested_role', 'status', 'created_at']
    list_filter = ['status', 'requested_role']
    search_fields = ['user__email', 'user__firstName', 'user__lastName']
    actions = ['approve_request', 'deny_request']

    def approve_request(self, request, queryset):
        for role_request in queryset:
            if role_request.status == 'Pending':
                user = role_request.user
                user.role = role_request.requested_role
                user.save()
                role_request.status = 'Approved'
                role_request.save()
                self.message_user(request, f"Approved role change for {user.email} to {user.role}")
    approve_request.short_description = "Approve selected role change requests"

    def deny_request(self, request, queryset):
        for role_request in queryset:
            if role_request.status == 'Pending':
                role_request.status = 'Denied'
                role_request.save()
                self.message_user(request, f"Denied role change for {role_request.user.email}")
    deny_request.short_description = "Deny selected role change requests"

admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.RoleChangeRequest, RoleChangeRequestAdmin)