from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.principal.as_view()), name="principal"),
    path('principal_ajax', login_required(views.principal_ajax), name="principal_ajax"),
    path('table_personas_ajax', login_required(views.table_personas_ajax), name="table_personas_ajax"),
]