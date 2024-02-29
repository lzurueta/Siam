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

        context = {
            'titulo': "OP Pagadas",
            'pagadas': pagadas,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

####################################################################################################
############################### VISTA DE DETALLE DE ORDEN DE COMPRA ################################
####################################################################################################

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

####################################################################################################
##################################### VISTA DE COMPROBANTE DE PAGO #################################
####################################################################################################

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

####################################################################################################
#################################### IMPRESOR DE OP ################################################
####################################################################################################
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

####################################################################################################
############### FUNCION PARA CONVERTIR NUMEROS DECIMALES A TEXTO (se usa en importe) ###############
####################################################################################################
def decimal_a_texto(numero):
    parte_entera = int(numero)
    parte_decimal = int((numero - parte_entera) * 100)  # Multiplica por 100 y convierte a entero
    texto_entero = num2words(parte_entera, lang='es')
    texto_decimal = num2words(parte_decimal, lang='es')

    if parte_decimal > 0:
        return f"{texto_entero} punto {texto_decimal}"
    else:
        return texto_entero

####################################################################################################
################ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA ######################
####################################################################################################

def op_pagadas_ajax(request):
    cuit = 30718402235

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    pagadas = CPOPAGO.objects.filter(cbencui=cuit)

    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        pagadas = pagadas.filter(cpopanio__icontains=request.POST.get('ejer_ajax'))
    # FILTRAR POR JURISDICCION
    if request.POST.get('jur_ajax'):
        pagadas = pagadas.filter(cjurcod__icontains=request.POST.get('jur_ajax'))
        # FILTRAR POR UNIDAD DE JURISDICCION
    if request.POST.get('udo_ajax'):
        pagadas = pagadas.filter(crepudo__icontains=request.POST.get('udo_ajax'))
        # FILTRAR POR UNIDAD NUMERO DE OP
    if request.POST.get('nro_op_ajax'):
        pagadas = pagadas.filter(copanro__icontains=request.POST.get('nro_op_ajax'))
        # FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax'):
        pagadas = pagadas.filter(cpopfpg__gte=request.POST.get('desde_ajax'))
    # FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax'):
        pagadas = pagadas.filter(cpopfpg__lte=request.POST.get('hasta_ajax'))
    # FILTRAR POR TIPOS DE CHEQUES
    if request.POST.get('cheque_ajax'):
        pagadas = pagadas.filter(cpoptip__lte=request.POST.get('cheque_ajax'))

    data = list(pagadas.values())
    return JsonResponse(data, safe=False)