from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('perfil', login_required(views.ProfileView.as_view()), name="userProfile"),
    path('logout_view', login_required(views.logout_view.as_view()), name="logout_view"),
    path('registrarse', views.registerUser, name="registrarUsuario"),

    path('recuperarContrasena', auth_views.PasswordResetView.as_view(template_name='registration/recPassword.html'), name="recuperarContrasena"),
    path('recuperarContrasenaEnviado', auth_views.PasswordResetDoneView.as_view(template_name='registration/recPasswordSend.html'), name="password_reset_done"),
    path('recuperarContrasenaReinicio/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/recPasswordReset.html'), name="password_reset_confirm"),
    path('recuperarContrasenaCompleto/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/recPasswordCompleted.html'), name="password_reset_complete"),


    path('', login_required(views.home.as_view()), name="home"),

]

