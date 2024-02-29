from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

from num2words import num2words

from proveedores.models import CPOPAGO
from sistema.functions import generate_pdf




# Create your views here.
class proveedoresHome(View):

    def get_context_data(self, **kwargs):
        context = {
            'titulo': "Home Proveedores",
        }
        return context

    def get(self, request, *args, **kwargs):
        template_name = 'proveedores/index.html'
        return render(request, template_name, self.get_context_data())


class op_pagadas(View):
    template_name = 'proveedores/op_pagadas.html'

    def get_context_data(self, **kwargs):
        cuit = 30718402235
        
        # ARMAR PRIMER OBJETO CON NRO DE CUIL
        pagadas = CPOPAGO.objects.filter(cbencui=cuit)
        # FILTRAR POR EJERCICIO 
        if self.request.POST.get('ejer'):
            pagadas = pagadas.filter(cpopanio__icontains=self.request.POST.get('ejer'))
        # FILTRAR POR JURISDICCION 
        if self.request.POST.get('jur'):
            pagadas = pagadas.filter(cjurcod__icontains=self.request.POST.get('jur'))    
        # FILTRAR POR UNIDAD DE JURISDICCION 
        if self.request.POST.get('udo'):
            pagadas = pagadas.filter(crepudo__icontains=self.request.POST.get('udo'))   
        # FILTRAR POR UNIDAD NUMERO DE OP 
        if self.request.POST.get('nro_op'):
            pagadas = pagadas.filter(copanro__icontains=self.request.POST.get('nro_op'))   
        # FILTRAR POR FECHA DESDE
        if self.request.POST.get('desde'):
            pagadas = pagadas.filter(cpopfpg__gte=self.request.POST.get('desde'))
        # FILTRAR POR FECHA HASTA
        if self.request.POST.get('hasta'):
            pagadas = pagadas.filter(cpopfpg__lte=self.request.POST.get('hasta'))
        # FILTRAR POR TIPOS DE CHEQUES
        if self.request.POST.get('cheque'):
            pagadas = pagadas.filter(cpoptip__lte=self.request.POST.get('cheque'))
            
        context = {
            'titulo': "OP Pagadas",
            'pagadas': pagadas,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


class op_pagadas_detalle(View):
    template_name = 'proveedores/op_pagadas_detalle.html'
    def get_context_data(self, **kwargs):

        op_pagada = CPOPAGO.objects.get(id=self.request.GET['id'])

        context = {
            'titulo': 'Detalle de la OP',
            'op_pagada': op_pagada,

        }
        return context
    def get(self, request, *args, **kwargs):
        data = dict()
        data['html_form'] = render_to_string(self.template_name, self.get_context_data(), request=request)
        return JsonResponse(data)


class op_pagadas_comprobante(View):
    template_name = 'proveedores/op_pagadas_comprobante.html'
    def get_context_data(self, **kwargs):

        op_pagada = CPOPAGO.objects.get(id=self.request.GET['id'])

        context = {
            'titulo': 'Comprobante de Pago',
            'op_pagada': op_pagada,

        }
        return context
    def get(self, request, *args, **kwargs):
        data = dict()
        data['html_form'] = render_to_string(self.template_name, self.get_context_data(), request=request)
        return JsonResponse(data)

class op_pagadas_imprimir(View):
    template_name = 'proveedores/op_pagadas_pdf.html'

    def get(self, request, *args, **kwargs):
        op_pagada = CPOPAGO.objects.get(id=kwargs['id'])

        if op_pagada.copaest == 1:
            estado_op = 'Cancelada'
        else:
            estado_op = 'Pendiente'
       
        context = {
            'op_pagada': op_pagada,
            'importeTexto': decimal_a_texto(op_pagada.cpopimp),
            'estado_op' : estado_op
        }
        
        return generate_pdf(request, self.template_name, context)


def decimal_a_texto(numero):
    parte_entera = int(numero)
    parte_decimal = int((numero - parte_entera) * 100)  # Multiplica por 100 y convierte a entero
    texto_entero = num2words(parte_entera, lang='es')
    texto_decimal = num2words(parte_decimal, lang='es')

    if parte_decimal > 0:
        return f"{texto_entero} punto {texto_decimal}"
    else:
        return texto_entero

def op_pagadas_ajax(request):
    ejer = request.GET.get('ejer_ajax', None)
    cuit = 30718402235

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    pagadas = CPOPAGO.objects.filter(cbencui=cuit)

    # FILTRAR POR EJERCICIO
    if request.GET.get('ejer_ajax'):
        pagadas = pagadas.filter(cpopanio__icontains=request.GET.get('ejer_ajax'))
    # FILTRAR POR JURISDICCION
    if request.GET.get('jur_ajax'):
        pagadas = pagadas.filter(cjurcod__icontains=request.GET.get('jur_ajax'))
        # FILTRAR POR UNIDAD DE JURISDICCION
    if request.GET.get('udo_ajax'):
        pagadas = pagadas.filter(crepudo__icontains=request.GET.get('udo_ajax'))
        # FILTRAR POR UNIDAD NUMERO DE OP
    if request.GET.get('nro_op_ajax'):
        pagadas = pagadas.filter(copanro__icontains=request.GET.get('nro_op_ajax'))
        # FILTRAR POR FECHA DESDE
    if request.GET.get('desde_ajax'):
        pagadas = pagadas.filter(cpopfpg__gte=request.GET.get('desde_ajax'))
    # FILTRAR POR FECHA HASTA
    if request.GET.get('hasta_ajax'):
        pagadas = pagadas.filter(cpopfpg__lte=request.GET.get('hasta_ajax'))
    # FILTRAR POR TIPOS DE CHEQUES
    if request.GET.get('cheque_ajax'):
        pagadas = pagadas.filter(cpoptip__lte=request.GET.get('cheque_ajax'))

    data = list(pagadas.values())
    return JsonResponse(data, safe=False)