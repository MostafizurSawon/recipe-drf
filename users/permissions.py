# users/permissions.py
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class RoleBasedPermission(permissions.BasePermission):
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        logger.info(f"User: {request.user}, Role: {getattr(request.user, 'role', 'Not set')}, Email: {getattr(request.user, 'email', 'Not set')}")
        if not request.user or not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access a role-based endpoint")
            return False
        user_role = getattr(request.user, 'role', None)
        if user_role is None:
            logger.error(f"User {getattr(request.user, 'email', 'Unknown')} has no role assigned")
            return False
        has_permission = user_role in self.allowed_roles
        if not has_permission:
            logger.warning(f"User {getattr(request.user, 'email', 'Unknown')} with role {user_role} "
                          f"attempted to access endpoint requiring roles {self.allowed_roles}")
        else:
            logger.info(f"User {getattr(request.user, 'email', 'Unknown')} with role {user_role} "
                       f"granted access to endpoint")
        return has_permission

# For views using get_permissions (e.g., CommentViewSet, ReviewViewSet)
def role_based_permission(allowed_roles):
    return RoleBasedPermission(allowed_roles=allowed_roles)  # Return an instance

# For views using permission_classes (e.g., AllUsersView, RecipesByUserView)
def role_based_permission_class(allowed_roles):
    class RoleBasedPermissionWithRoles(RoleBasedPermission):
        def __init__(self):
            super().__init__(allowed_roles=allowed_roles)
    return RoleBasedPermissionWithRoles  # Return the class