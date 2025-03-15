import random
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()

class UserRegistrationView(APIView):
    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "User Registration Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            print(serializer.errors)
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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_data = UserProfileSerializer(user).data
        return Response(
            {
                "status": "success",
                "message": "Request Successful",
                "data": user_data,
            },
            status=status.HTTP_200_OK,
        )

class UserProfileUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=UserProfileSerializer)
    def post(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "Request Successful"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "failed", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
