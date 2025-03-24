# users/urls.py
from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, SendOTPView,
    VerifyOTPView, ResetPasswordView, UserProfileView, 
    UserProfileUpdateView, ValidatePasswordView,
    RoleChangeRequestView, AllUsersView, SpecificUserProfileView, UpdateUserRoleView
)

urlpatterns = [
    # Authentication and user management
    path('register/', UserRegistrationView.as_view(), name='register'),  # Register a new user
    path('login/', UserLoginView.as_view(), name='login'),  # User login
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),  # Send OTP for password reset
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),  # Verify OTP for password reset
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),  # Reset password after OTP verification
    path('validate-password/', ValidatePasswordView.as_view(), name='validate_password'),  # Validate user credentials

    # User profile management
    path('profile/', UserProfileView.as_view(), name='profile'),  # Get current user's profile
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),  # Update current user's profile

    # Role management
    path('role-change-request/', RoleChangeRequestView.as_view(), name='request_role_change'),  # Submit a role change request

    # Admin user management
    path('profile/all/', AllUsersView.as_view(), name='all_users'),  # Get all users (admin only)
    path('profile/<str:email>/', SpecificUserProfileView.as_view(), name='specific_user_profile'),  # Get a specific user's profile (admin only)
    path('profile/<str:email>/update-role/', UpdateUserRoleView.as_view(), name='update_user_role'),
]