from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializer import (UserRegistrationSerializer,
                         UserLoginSerializer,
                         UserChangePasswordSerializer,
                         SendPasswordResetEmailSerializer,
                         PasswordOTPVerifySerializer,
                         PasswordResetSerializer,
                         UserProfileSerializer,
                         ProfileOnboardSerializer,
                         VerifyAccountSerializer,
                         UserProfileSerializer,
                         )
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .email import send_verify_user_token_via_email
from .models import User, UserProfile, UserOnboard
from datetime import date, datetime


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class TestAPI(APIView):
    def get(self, request, format=None):
        return Response({'msg': 'Aquatrack is Running'})


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if len(serializer.validated_data['password']) >= 8:
            user = serializer.save()
            send_verify_user_token_via_email(serializer.data['email'])
            UserProfile.objects.create(
                user_id = user,
                first_name = serializer.data['name'],
                email=serializer.data['email'],
                created_at = datetime.today(),
            )
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Please Set Password Minimum 8 Characters long'}, status=status.HTTP_201_CREATED)


class VerifyOTP(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                global user
                user = User.objects.filter(email=email)
                if not user.exists():
                    return Response({'errors': "something went wrong user not found"}, status=status.HTTP_404_NOT_FOUND)
                if user[0].email_verification_token != otp:
                    return Response({'errors': "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
                User.objects.filter(email=email).update(
                    is_verified_account=True, email_verified_at=date.today())
                user = User.objects.get(email=email)
                token = get_tokens_for_user(user)
                return Response({'token': token, 'Success': "OTP Varified Sucessfully"}, status=status.HTTP_200_OK)
            return Response({'errors': "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': 'Email or Password is not Valid'}, status=status.HTTP_404_NOT_FOUND)


class UserChangePassword(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmail(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


class VerifyResetPasswordOTP(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = PasswordOTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'OTP Verified Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Somethig Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileOnboard(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if UserOnboard.objects.filter(user_id=request.user.id).exists():
            data = UserOnboard.objects.filter(user_id=request.user.id)
            serializer = ProfileOnboardSerializer(data,many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "Profile Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request, format=None):
        try:
            if UserOnboard.objects.filter(user_id=request.user.id).exists():
                return Response({'error': 'Profile Already Exist'}, status=status.HTTP_403_FORBIDDEN)
            else:
                serializer = ProfileOnboardSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(user_id=request.user)
                    return Response({'msg': 'Profile Created Successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_200_OK)


    def put(self, request, pk=None):
        if UserOnboard.objects.filter(user_id=request.user.id).exists():
            data = UserOnboard.objects.get(user_id=request.user.id)
            serializer = ProfileOnboardSerializer(
                data=request.data, instance=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=datetime.today())
            return Response({'msg': 'Profile Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "Profile Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)



class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if UserProfile.objects.filter(user_id=request.user).exists():
            user = UserProfile.objects.get(user_id=request.user)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "Profile Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None):
        if UserProfile.objects.filter(user_id=request.user).exists():

            profile = UserProfile.objects.get(user_id=request.user.id)
            serializer = UserProfileSerializer(
                data=request.data, instance=profile, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user_id=request.user)
            return Response({'msg': 'Profile Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "Profile Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
