from django.shortcuts import render
from django.views import View
from sistema.functions import traerIndex
from django.http import JsonResponse, HttpResponse

from .forms import registroContrato

from django.db.models import F, Func, Value, CharField

from .models import Contrato, Medio, Reparticion

from django.contrib.auth.models import User

from sistema.functions import generate_pdf

from sistema.models import Profile

# Create your views here.

class contratos(View):
    template_name = 'prensa/contratos.html'

    def get_context_data(self, **kwargs):

        form = registroContrato()

        context = {
            'titulo': "Contratos",
            'index': traerIndex(self.request),
            'form': form
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


class contratos_ajax(View):
    """COMPLETAR DATOS DE TABLA DE CONTRATOS"""
    def post(self, request):
        contrato = Contrato.objects.annotate(
        monto_formateado=Func( F('monto'), Value('9G999G999G999D99'), function='TO_CHAR', output_field=CharField()),
        fechaInicio_formateada=Func(F('fechaInicio'), Value('DD-MM-YYYY'), function='TO_CHAR', output_field=CharField()),
        fechaFin_formateada=Func(F('fechaFin'), Value('DD-MM-YYYY'), function='TO_CHAR', output_field=CharField())
        ).values(
        'id',
        'user__profile__nombre',
        'user__username',
        'medio__nombre',
        'programa',
        'monto_formateado',
        'reparticion__nombre',
        'fechaInicio_formateada',
        'fechaFin_formateada',
        'status'
        )
        data = list(contrato)
        return JsonResponse(data, safe=False)


def guardarFormContrato(request):
    form = registroContrato(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario_id = form.cleaned_data.get('usuario')
        proveedor = User.objects.filter(id=usuario_id).first()
        medio = Medio.objects.filter(id=form.cleaned_data.get('medio')).first()
        programa = form.cleaned_data.get('programa')
        reparticion = Reparticion.objects.filter(id=form.cleaned_data.get('reparticion')).first()
        monto = form.cleaned_data.get('monto')
        fechaInicio = form.cleaned_data.get('fecha_inicio')
        fechaFin = form.cleaned_data.get('fecha_fin')


        contrato = Contrato.objects.create(user = proveedor, medio = medio, programa = programa, reparticion = reparticion, monto = monto, fechaInicio = fechaInicio, fechaFin = fechaFin, status = 'P')

        return HttpResponse()

def contrato_pdf(request):
    """ IMPRESOR DE CONTRATO """
    template_name = 'prensa/contrato_pdf.html'

    id = request.POST.get('id')
    contrato = Contrato.objects.get(id = id)
    profile = Profile.objects.get(user = contrato.user)
    context = {
        'contrato': contrato,
        'profile': profile
    }

    return generate_pdf(request, template_name, context)

def autorizar_contrato(request):
    contrato = Contrato.objects.get(pk=request.POST.get('id'))
    contrato.status = 'A'
    contrato.save()

    return HttpResponse()

def denegar_contrato(request):
    contrato = Contrato.objects.get(pk=request.POST.get('id'))
    contrato.status = 'D'
    contrato.save()

    return HttpResponse()