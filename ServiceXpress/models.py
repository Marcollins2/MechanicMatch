from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, confirm_password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        # Check that the passwords match
        if password != confirm_password:
            raise ValidationError(_("Passwords do not match"))

        # Optionally, use Django's built-in password validation
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            raise ValidationError(_("Password is not valid: ") + str(e))
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=None)
    is_staff = models.BooleanField(default=None)
    USER_TYPE_CHOICES = (
        ('', '---------'),
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='')


    # Add related_name attributes to avoid conflicts with Django's auth.User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='servicexpress_user_groups',  # Custom related name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='servicexpress_user_permissions',  # Custom related name
        blank=True
    )

    objects = UserManager()



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    category = models.CharField(max_length=100, choices=[('washing','washing'),('repair', 'repair'),('maintenance','maintenance')]) 
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ],
        default='pending'
    )
    time = models.DateTimeField(auto_now_add=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    media = models.FileField(upload_to='service_media/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    service_provider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests',
        limit_choices_to={'is_active': True}
    )
    urgency_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )

    def __str__(self):
        return f"{self.category} for {self.user.email} - {self.status}"


