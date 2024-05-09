from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.principal.as_view()), name="principal"),
    path('principal_ajax', login_required(views.principal_ajax), name="principal_ajax"),
    path('table_personas_ajax', login_required(views.table_personas_ajax), name="table_personas_ajax"),
    path('table_categorias_ajax', login_required(views.table_categorias_ajax), name="table_categorias_ajax"),
    path('table_conceptos_ajax', login_required(views.table_conceptos_ajax), name="table_conceptos_ajax"),
]