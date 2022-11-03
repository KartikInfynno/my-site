from rest_framework import serializers
from .models import User, PasswordResets, UserOnboard, UserProfile
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .email import send_password_reset_token_via_email
from django.contrib.auth import authenticate


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'is_verified_account']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class UserChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        password = attrs.get('password')
        user = self.context.get('user')
        auth = authenticate(email=user.email, password=current_password)
        if auth:
            user.set_password(password)
            user.save()
        else:
            raise serializers.ValidationError('Current Password is invalid')
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            subject = "Password Reset OTP"
            send_password_reset_token_via_email(user.email, subject)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')



class PasswordOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    otp = serializers.CharField(max_length=6)

    class Meta:
        fields = ['otp', 'email']

    def validate(self, attrs):
        try:
            otp = attrs.get('otp')
            email = attrs.get('email')
            user = User.objects.get(email=email)
            reset = PasswordResets.objects.get(user_email=user.id)
            if otp == reset.otp_token and user == reset.user_email:
                reset.is_verified_token = True
                reset.save()
                return attrs
            else:
                raise serializers.ValidationError('Invalid OTP')
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError('Invalid OTP')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'email']
    
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            email= attrs.get('email')
            user = User.objects.get(email=email)
            reset = PasswordResets.objects.get(user_email=user.id)
            if reset.is_verified_token:
                user.set_password(password)
                user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError('Something Went wrong')
    
class ProfileOnboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOnboard
        fields = ['gender', 'birth_date', 'weight',
                  'weight_unit', 'activity_level', 'weather_condition']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ['id','user_id', 'created_at', 'updated_at']
