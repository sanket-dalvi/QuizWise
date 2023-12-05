from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

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
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=15, unique=True, validators=[RegexValidator(r'^\d{10}$', message='Contact number must be 10 digits.')])
    password = models.CharField(max_length=128)  # Will store hashed passwords

    # New field for role selection
    is_examinee = models.BooleanField(default=False)
    is_examiner = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)
    mobile_notification = models.BooleanField(default=False)


    # Update groups field with unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='quizwise_user_groups',  # Unique related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )

    # Update user_permissions field with unique related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='quizwise_user_permissions',  # Unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
    )


    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'contact']

    def save(self, *args, **kwargs):
        # Encrypt password before saving
        if self.password.startswith('pbkdf2_sha256$'):
            # Password already encrypted (in case of updating user profile)
            pass
        else:
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=6)  # Assuming OTPs are 6 characters long
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"
    

    

