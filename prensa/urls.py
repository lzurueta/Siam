from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.contratos.as_view()), name="contratos"),
    path('contratos_ajax', login_required(views.contratos_ajax.as_view()),name="contratos_ajax"),
    path('submitContrato', login_required(views.guardarFormContrato), name="submitContrato"),
    path('contrato_pdf', login_required(views.contrato_pdf), name="contrato_pdf"),
    path('autorizar_contrato', login_required(views.autorizar_contrato), name="autorizar_contrato"),
    path('denegar_contrato', login_required(views.denegar_contrato), name="denegar_contrato"),
    path('datos_graficos', login_required(views.datos_graficos), name="datos_graficos"),


    path('auditoria', login_required(views.auditoria.as_view()), name="auditoria"),
    path('auditoria_ajax', login_required(views.auditoria_ajax.as_view()),name="auditoria_ajax"),
]
