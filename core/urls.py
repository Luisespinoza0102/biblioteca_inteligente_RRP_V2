from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Inicio y Auth
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),

    # Notificaciones e Historial
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificaciones/leer/<int:noti_id>/', views.marcar_leida, name='marcar_leida'),
    path('mi-historial/', views.mi_historial, name='mi_historial'),
    
    # Gestión de usuarios (Lista Blanca)
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/editar/<uuid:user_id>/', views.editar_usuario, name='editar_usuario'),
    
    path('mi_perfil/', views.mi_perfil, name='mi_perfil'),
    path('configuracion/seguridad/', views.CambiarPasswordView.as_view(), name='cambiar_password'),
    
    # 1. Formulario donde pones el correo
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="core/registration/password_reset.html"), name="reset_password"),
    
    # 2. Mensaje de "Te enviamos un correo"
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="core/registration/password_reset_sent.html"), name="password_reset_done"),
    
    # 3. El enlace que llega al correo (el token de seguridad)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="core/registration/password_reset_form.html"), name="password_reset_confirm"),
    
    # 4. Mensaje de "Contraseña cambiada con éxito"
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="core/registration/password_reset_done.html"), name="password_reset_complete"),
]