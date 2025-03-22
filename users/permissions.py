from rest_framework import permissions

class RoleBasedPermission(permissions.BasePermission):
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        # Allow access if the user is authenticated and their role is in allowed_roles
        return (request.user 
                and request.user.is_authenticated 
                and request.user.role in self.allowed_roles)

# Factory function to create RoleBasedPermission instances
def role_based_permission(allowed_roles):
    class RoleBasedPermissionInstance(RoleBasedPermission):
        def __init__(self):
            super().__init__(allowed_roles=allowed_roles)
    return RoleBasedPermissionInstance