from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.administracion_usuarios.as_view()),name="administracion_usuarios"),
    path('administracion_usuarios_ajax', login_required(views.administracion_usuarios_ajax.as_view()), name="administracion_usuarios_ajax"),
    path('administracion_usuarios_estado', login_required(views.administracion_usuarios_estado), name="administracion_usuarios_estado"),
    path('administracion_usuarios_actualizar_clave', login_required(views.administracion_usuarios_actualizar_clave),name="administracion_usuarios_actualizar_clave"),
    path('imprimir_dj', login_required(views.imprimir_dj), name="imprimir_dj"),
    path('administracion_observacion', login_required(views.administracion_observacion), name="administracion_observacion"),
    path('administracion_actualizar_observacion', login_required(views.administracion_actualizar_observacion), name="administracion_actualizar_observacion")
]
