from django.urls import path
from .views import (
    RegisterView, VerifyEmailView, ProfileView,
    ChangePasswordView, ResetPasswordRequestView, ResetPasswordConfirmView,GetUserByEmailView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),

    # JWT endpoints (SimpleJWT)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Logout (blacklist) - SimpleJWT provides a view if you install blacklist app
    # You may create a custom logout that blacklists refresh token.

    # Profile
    path("me/", ProfileView.as_view(), name="user-profile"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),

    # Password reset
    path("password/reset/", ResetPasswordRequestView.as_view(), name="password-reset-request"),
    path("password/reset/confirm/", ResetPasswordConfirmView.as_view(), name="password-reset-confirm"),
    path("users/by-email/", GetUserByEmailView.as_view(), name="user-by-email"),
]

from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns += router.urls