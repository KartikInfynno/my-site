from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('verify/account/', views.VerifyOTP.as_view()),
    path('profile/onboard/', views.UserProfileOnboard.as_view()),
    path('profile/', views.UserProfileView.as_view(),),
    path('update/profile/', views.UserProfileView.as_view()),
    path('change/password/', views.UserChangePassword.as_view()),
    path('password/reset/email/', views.SendPasswordResetEmail.as_view()),
    path('password/reset/otp/', views.VerifyResetPasswordOTP.as_view()),
    path('password/reset/', views.ResetPassword.as_view()),
        path('resend/verification/token/', views.ResendVarificationEmail.as_view()),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
]
