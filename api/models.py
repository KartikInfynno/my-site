from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from .manager import UserManager


class User(AbstractUser):
    username = None
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    email_verified_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_account = models.BooleanField(default=False)
    email_verification_token = models.CharField(
        max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class PasswordResets(models.Model):
    user_email = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=191)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_token = models.BooleanField(default=False)

    def __str__(self):
        return self.user_email.email


gender_choice = (
    ('male', 'male'),
    ('female', 'female')

)
weight_unit = (
    ('kg', 'kg'),
    ('lbs', 'lbs')

)
activity_level = (
    ('low', 'low'),
    ('intermediate', 'intermediate'),
    ('advanced', 'advanced')
)
weather_type = (
    ('hot', 'hot'),
    ('mild', 'mild'),
    ('cold', 'cold')
)


class UserOnboard(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=10, choices=gender_choice, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    weight_unit = models.CharField(
        max_length=5, choices=weight_unit, blank=True, null=True)
    activity_level = models.CharField(
        max_length=12, choices=activity_level, blank=True, null=True)
    weather_condition = models.CharField(
        max_length=7, choices=weather_type, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user_id.email

def upload_course_cover(object, filename):
    return '/media/user_profile_picture/%s_%s' % (UserProfile.objects.aggregate(max('id'))['id__max'] + 1, filename)
class UserProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    user_profile_picture = models.ImageField(
        blank=True, null=True, upload_to='user_profile_picture',)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    contact = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
