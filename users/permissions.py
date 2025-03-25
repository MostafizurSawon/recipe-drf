# users/permissions.py
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class RoleBasedPermission(permissions.BasePermission):
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        # Debug user attributes
        logger.info(f"User: {request.user}, Role: {getattr(request.user, 'role', 'Not set')}, Email: {getattr(request.user, 'email', 'Not set')}")
        # Allow access if the user is authenticated and their role is in allowed_roles
        has_permission = (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in self.allowed_roles
        )
        if not has_permission:
            logger.warning(f"User {getattr(request.user, 'email', 'Unknown')} with role {getattr(request.user, 'role', 'Unknown')} "
                          f"attempted to access endpoint requiring roles {self.allowed_roles}")
        else:
            logger.info(f"User {getattr(request.user, 'email', 'Unknown')} with role {getattr(request.user, 'role', 'Unknown')} "
                       f"granted access to endpoint")
        return has_permission

# Factory function to create RoleBasedPermission classes
def role_based_permission(allowed_roles):
    class RoleBasedPermissionWithRoles(RoleBasedPermission):
        def __init__(self):
            super().__init__(allowed_roles=allowed_roles)
    return RoleBasedPermissionWithRoles