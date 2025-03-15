from rest_framework import serializers
from .models import User, UserProfile

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ["image", "age", "portfolio", "sex", "bio", "facebook"]
#         extra_kwargs = {
#             "image": {"required": False},
#             "portfolio": {"required": False},
#             "facebook": {"required": False},
#         }

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "mobile"]
        # extra_kwargs = {"email": {"read_only": True}}

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
        UserProfile.objects.create(user=user)  # Default profile
        return user

class UserFullSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "mobile", "profile"]
        extra_kwargs = {
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        profile = instance.profile

        instance.firstName = validated_data.get("firstName", instance.firstName)
        instance.lastName = validated_data.get("lastName", instance.lastName)
        instance.mobile = validated_data.get("mobile", instance.mobile)
        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance