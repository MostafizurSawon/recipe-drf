# users/models.py (Full Code)
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_verified = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "Admin")
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Chef', 'Chef'),
        ('User', 'User'),
    )

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    mobile = models.CharField(max_length=14, blank=True, null=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_verification_sent = models.DateTimeField(null=True, blank=True)  # New field

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstName", "lastName"]

    objects = UserManager()

    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.email})"

SEX_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='users/images/', blank=True, null=True)
    age = models.IntegerField(default=18)
    portfolio = models.URLField(blank=True, null=True)
    sex = models.CharField(choices=SEX_CHOICES, max_length=10, default="Male")
    bio = models.TextField(blank=True)
    facebook = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.firstName} {self.user.lastName}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class RoleChangeRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_change_requests')
    requested_role = models.CharField(max_length=10, choices=User.ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(blank=True, help_text="Reason for requesting this role")

    def __str__(self):
        return f"{self.user.email} - Request to be {self.requested_role} ({self.status})"

    class Meta:
        verbose_name = "Role Change Request"
        verbose_name_plural = "Role Change Requests"