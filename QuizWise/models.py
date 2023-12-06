from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from .constants import (
    USER_FIELDS,
    USER_GROUPS_RELATED_NAME,
    USER_PERMISSIONS_RELATED_NAME,
    OTP_LENGTH,
    EMAIL_HELP_TEXT,
    USERNAME_HELP_TEXT,
    FIRST_NAME_HELP_TEXT,
    LAST_NAME_HELP_TEXT,
    CONTACT_HELP_TEXT,
    GROUPS_HELP_TEXT,
    USER_PERMISSIONS_HELP_TEXT,
    EMAIL_VALUE_ERROR,
    USERNAME_VALUE_ERROR,
    CONTACT_VALUE_ERROR,
)

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(EMAIL_VALUE_ERROR)
        if not username:
            raise ValueError(USERNAME_VALUE_ERROR)

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, help_text=EMAIL_HELP_TEXT)
    username = models.CharField(max_length=150, unique=True, help_text=USERNAME_HELP_TEXT)
    first_name = models.CharField(max_length=150, help_text=FIRST_NAME_HELP_TEXT)
    last_name = models.CharField(max_length=150, help_text=LAST_NAME_HELP_TEXT)
    contact = models.CharField(max_length=15, unique=True, validators=[RegexValidator(r'^\d{10}$', message=CONTACT_VALUE_ERROR)])
    password = models.CharField(max_length=128)  # Will store hashed passwords

    # New field for role selection
    is_examinee = models.BooleanField(default=False)
    is_examiner = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)
    mobile_notification = models.BooleanField(default=False)


    # Update groups field with unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name=USER_GROUPS_RELATED_NAME, 
        blank=True,
        help_text=GROUPS_HELP_TEXT,
    )

    # Update user_permissions field with unique related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name=USER_PERMISSIONS_RELATED_NAME,
        blank=True,
        help_text=USER_PERMISSIONS_HELP_TEXT,
    )

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = USER_FIELDS

    def save(self, *args, **kwargs):
        # Encrypt password before saving
        if self.password.startswith('pbkdf2_sha256$'):
            pass
        else:
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=OTP_LENGTH) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"
    

    

