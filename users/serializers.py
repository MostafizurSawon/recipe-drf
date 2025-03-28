import logging
from rest_framework import serializers
from .models import User, UserProfile, RoleChangeRequest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "role"]
        ref_name = 'UsersUserSerializer'

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["image", "age", "portfolio", "sex", "bio", "facebook", "user"]
        extra_kwargs = {
            "image": {"required": False},
            "portfolio": {"required": False},
            "facebook": {"required": False},
            "age": {"required": False, "allow_null": True},
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "password", "mobile"]
        extra_kwargs = {
            "email": {"required": True, "validators": [serializers.EmailField().validators[0]]},
            "firstName": {"required": True},
            "lastName": {"required": True},
            "mobile": {"required": False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        logger.info(f"User {user.email} saved successfully")

        # Email verification
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_link = f"https://recipe-drf.onrender.com/accounts/activate/{uid}/{token}/"  
        # confirm_link = f"http://127.0.0.1:8000/users/activate/{uid}/{token}/"  
        
        send_mail(
            subject="Verify Your Email",
            message=f"Please click this link to verify your email: {confirm_link}",
            from_email="Recipe Hub <no-reply@recipehub.com>",
            recipient_list=[user.email],
        )
        logger.info(f"Verification email sent to {user.email}")
        return user

class UserFullSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "mobile", "role", "profile", "password"]
        extra_kwargs = {
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)

        try:
            profile = instance.profile
        except User.profile.RelatedObjectDoesNotExist:
            profile = UserProfile.objects.create(user=instance)

        instance.firstName = validated_data.get("firstName", instance.firstName)
        instance.lastName = validated_data.get("lastName", instance.lastName)
        instance.mobile = validated_data.get("mobile", instance.mobile)
        instance.role = validated_data.get("role", instance.role)

        if password:
            instance.set_password(password)

        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    
    def validate_password(self, value):
        if value and not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value

class RoleChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleChangeRequest
        fields = ["requested_role", "reason"]
        extra_kwargs = {
            "reason": {"required": False},
        }

    def validate_requested_role(self, value):
        if value == 'User':
            raise serializers.ValidationError("You are already a User. Please request a different role.")
        return value
    
class RoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    def validate_role(self, value):
        if value not in dict(User.ROLE_CHOICES):
            raise serializers.ValidationError("Invalid role. Must be Admin, Chef, or User.")
        return value