from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from users.apps import UsersConfig
from .views import RegisterView, ProfileUserDetailView, ProfileUserUpdateView, CustomPasswordChangeView, \
    EmailVerificationView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/<str:token>/", EmailVerificationView.as_view(), name="verify_email"),

    path("profile/edit/", ProfileUserUpdateView.as_view(), name="profile_edit"),
    path("profile/", ProfileUserDetailView.as_view(), name="profile_user"),

    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name="users/password_change_done.html",
    ), name='password_change_done'),

    path('password-reset/',
         PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]
