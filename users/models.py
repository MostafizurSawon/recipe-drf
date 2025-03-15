from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    mobile = models.CharField(max_length=14, blank=True, null=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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