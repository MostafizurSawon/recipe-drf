from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class RoleBasedPermission(permissions.BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access a role-based endpoint")
            return False

        # Check if the user's role is in the allowed roles
        user_role = request.user.role
        has_permission = user_role in self.allowed_roles
        if not has_permission:
            logger.warning(f"User {request.user.email} with role {user_role} attempted to access endpoint requiring roles {self.allowed_roles}")
        else:
            logger.info(f"User {request.user.email} with role {user_role} granted access to endpoint")
        return has_permission

def role_based_permission(allowed_roles):
    return RoleBasedPermission(allowed_roles)