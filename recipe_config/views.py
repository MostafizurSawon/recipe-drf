import os
from django.http import HttpResponse
# from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.conf import settings
import logging
from django.http import HttpResponseNotFound
from django.template import loader
from django.urls import reverse

logger = logging.getLogger(__name__)

# Restrict access to superusers only
# @user_passes_test(lambda u: u.is_superuser)
def download_database(request):
    try:
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at {db_path}")
            return HttpResponse("Database file not found.", status=404)

        with open(db_path, 'rb') as db_file:
            db_data = db_file.read()

        # Response with the database file as a download
        response = HttpResponse(db_data, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="db.sqlite3"'
        response['Content-Length'] = len(db_data)

        logger.info("Database downloaded successfully by user: %s", request.user)
        return response

    except Exception as e:
        logger.error("Error downloading database: %s", str(e))
        return HttpResponse(f"Error downloading database: {str(e)}", status=500)
    



def custom_accounts(request, exception):
    # List of endpoints under 'accounts/'
    account_endpoints = [
        {"name": "Register", "url": reverse("register"), "description": "Register a new user"},
        {"name": "Login", "url": reverse("login"), "description": "Login to get a JWT token"},
        {"name": "Activate Email", "url": "accounts/activate/<str:uidb64>/<str:token>/", "description": "Activate your email"},
        {"name": "Resend Verification", "url": reverse("resend_verification"), "description": "Resend email verification link"},
        {"name": "Send OTP", "url": reverse("send_otp"), "description": "Send OTP for password reset"},
        {"name": "Verify OTP", "url": reverse("verify_otp"), "description": "Verify OTP to get a token"},
        {"name": "Reset Password", "url": reverse("reset_password"), "description": "Reset your password (requires authentication)"},
        {"name": "Validate Password", "url": reverse("validate_password"), "description": "Validate email and password"},
        {"name": "Profile", "url": reverse("profile"), "description": "Get your profile (requires authentication)"},
        {"name": "Profile Update", "url": reverse("profile_update"), "description": "Update your profile (requires authentication)"},
        {"name": "Role Change Request", "url": reverse("request_role_change"), "description": "Request a role change (requires authentication)"},
        {"name": "All Users", "url": reverse("all_users"), "description": "List all users (Admin only)"},
        {"name": "Specific User Profile", "url": "accounts/profile/<str:email>/", "description": "Get a specific user's profile (requires authentication)"},
        {"name": "Update User Role", "url": "accounts/profile/<str:email>/update-role/", "description": "Update a user's role (Admin only)"},
    ]

    context = {
        "account_endpoints": account_endpoints,
        "swagger_url": reverse("schema-swagger-ui"),
    }
    template = loader.get_template("accounts.html")
    return HttpResponseNotFound(template.render(context, request))