from django.urls import path
from . import views
from .views import RegisterView, LoginView,  LogoutView, AllUsersView, UpdateUserView, DeleteUserView, ValidateTokenView,  HomeView, VerifyEmail, PasswordTokenCheckAPI, RequestPasswordResetEmail, SetNewPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('users/', AllUsersView.as_view(), name='users'),
    path('user/<int:id>/update/', UpdateUserView.as_view(), name='update_user'),
    path('user/<int:id>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path('token/validate/', ValidateTokenView.as_view(), name='token_validate'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/',SetNewPasswordView.as_view(), name='password-reset-complete')
]

