from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, SendOTPView,
    VerifyOTPView, ResetPasswordView, UserProfileView, 
    UserProfileUpdateView, ValidatePasswordView,
    RoleChangeRequestView, AllUsersView, SpecificUserProfileView, 
    UpdateUserRoleView, ActivateEmailView, ResendVerificationView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('activate/<str:uidb64>/<str:token>/', ActivateEmailView.as_view(), name='activate'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('validate-password/', ValidatePasswordView.as_view(), name='validate_password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('role-change-request/', RoleChangeRequestView.as_view(), name='request_role_change'),
    path('profile/all/', AllUsersView.as_view(), name='all_users'),
    path('profile/<str:email>/', SpecificUserProfileView.as_view(), name='specific_user_profile'),
    path('profile/<str:email>/update-role/', UpdateUserRoleView.as_view(), name='update_user_role'),
]