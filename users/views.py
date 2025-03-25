import random
import logging
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserFullSerializer,
    RoleChangeRequestSerializer , RoleUpdateSerializer 
)
from .permissions import role_based_permission_class
from .models import RoleChangeRequest 

# Ensure logger is defined
logger = logging.getLogger(__name__)

User = get_user_model()

class UserRegistrationView(APIView):
    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered with email {user.email} and role {user.role}")
            return Response(
                {"status": "success", "message": "User Registration Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.error(f"User registration failed: {serializer.errors}")
            return Response(
                {"status": "Error", "message": "User Registration failed!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserLoginView(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ))
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": "success",
                    "message": "User Login Successful",
                    "token": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "unauthorized", "message": "Invalid Credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

class SendOTPView(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
        }
    ))
    def post(self, request):
        email = request.data.get("email")
        if not email or not User.objects.filter(email=email).exists():
            return Response(
                {"status": "failed", "message": "Valid Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = str(random.randint(1000, 9999))
        user = User.objects.get(email=email)
        user.otp = otp
        user.save()

        send_mail(
            subject="OTP for Password Reset",
            message=f"Your OTP is {otp}",
            from_email="X-Bakery OTP<otpxbakery@example.com>",
            recipient_list=[email],
        )

        return Response(
            {"status": "success", "message": "OTP Sent Successfully"},
            status=status.HTTP_200_OK,
        )

class VerifyOTPView(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
            'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP'),
        }
    ))
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"status": "failed", "message": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, otp=otp)
            user.otp = None
            user.save()

            token = str(RefreshToken.for_user(user).access_token)
            return Response(
                {
                    "status": "success",
                    "message": "OTP Verification Successful",
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": "failed", "message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ResetPasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='New Password'),
        }
    ))
    def post(self, request):
        password = request.data.get("password")

        if not password:
            return Response(
                {"status": "failed", "message": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.set_password(password)
        user.save()
        return Response(
            {"status": "success", "message": "Password Reset Successfully"},
            status=status.HTTP_200_OK,
        )

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the authenticated user's profile.",
        responses={
            200: openapi.Response('User profile', UserFullSerializer),
            401: 'Unauthorized',
        }
    )
    def get(self, request):
        user = request.user
        serializer = UserFullSerializer(user)
        return Response(
            {
                "status": "success",
                "message": "Request Successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class UserProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile.",
        request_body=UserFullSerializer,
        responses={
            200: openapi.Response('Updated user profile', UserFullSerializer),
            400: 'Bad Request',
            401: 'Unauthorized',
        }
    )
    def put(self, request):
        user = request.user

        # Handle both JSON and FormData
        if "multipart/form-data" in request.headers.get("Content-Type", "").lower():
            # Parse FormData into a nested dictionary
            data = {}
            profile_data = {}
            for key, value in request.data.items():
                if key.startswith("profile."):
                    profile_field = key.split("profile.")[1]
                    profile_data[profile_field] = value
                else:
                    data[key] = value
            if profile_data:
                data["profile"] = profile_data
        else:
            # JSON data, use as-is
            data = request.data

        # Debug: Log the parsed data
        logger.debug(f"Data to update: {data}")

        serializer = UserFullSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User profile updated for {user.email}")
            return Response(
                {
                    "status": "success",
                    "message": "Profile Updated Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        logger.error(f"Profile update failed for {user.email}: {serializer.errors}")
        return Response(
            {
                "status": "failed",
                "message": "Profile Update Failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class AllUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, role_based_permission_class(allowed_roles=['Admin'])]

    def get(self, request):
        users = User.objects.all()
        serializer = UserFullSerializer(users, many=True)
        return Response(
            {
                "status": "success",
                "message": "Request Successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class SpecificUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Removed admin restriction

    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
            serializer = UserFullSerializer(user)
            return Response(
                {
                    "status": "success",
                    "message": "Request Successful",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": "failed", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

class ValidatePasswordView(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ))
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"status": "failed", "message": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)

        if user:
            return Response(
                {"status": "valid", "message": "Credentials are valid"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "invalid", "message": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

class RoleChangeRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=RoleChangeRequestSerializer)
    def post(self, request):
        user = request.user
        # Check if the user already has a pending request
        if RoleChangeRequest.objects.filter(user=user, status='Pending').exists():
            return Response(
                {"status": "failed", "message": "You already have a pending role change request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RoleChangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            RoleChangeRequest.objects.create(
                user=user,
                requested_role=serializer.validated_data['requested_role'],
                reason=serializer.validated_data.get('reason', '')
            )
            logger.info(f"Role change request submitted by {user.email} for role {serializer.validated_data['requested_role']}")
            return Response(
                {"status": "success", "message": "Role change request submitted successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": "failed", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class UpdateUserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, role_based_permission_class(allowed_roles=['Admin'])]

    def put(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"User with email {email} not found for role update")
            return Response(
                {"status": "failed", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RoleUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "failed", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_role = serializer.validated_data["role"]
        if user.role == new_role:
            return Response(
                {"status": "failed", "message": f"User is already a {new_role}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.role = new_role
        user.save()
        logger.info(f"User {user.email} role updated to {new_role} by admin {request.user.email}")
        return Response(
            {"status": "success", "message": f"User role updated to {new_role} successfully"},
            status=status.HTTP_200_OK,
        )