from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View

from num2words import num2words


from proveedores.models import CPOPAGO
from sistema.functions import generate_pdf, conectarSQL


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
        cuit = 30718402234
        pagadas = CPOPAGO.objects.filter(cbencui=cuit)
        if self.request.POST.get('nro_op'):
            pagadas = pagadas.filter(copanro=self.request.POST.get('nro_op'))
        if self.request.POST.get('desde'):
            pagadas = pagadas.filter(cpopfpg__gte=self.request.POST.get('desde'))
        cuit = 30718402235
        anio = timezone.now().year

        # ARMAR PRIMER OBJETO CON NRO DE CUIL
        conexion = conectarSQL()
        cursor = conexion.cursor(as_dict=True)
        sql_query = ("SELECT * FROM POPAGO INNER JOIN OPAGO2 ON POPAGO.OpaAnio=OPAGO2.OpaAnio "
                     "AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod "
                     "AND POPAGO.repudo=OPAGO2.repudo WHERE POPAGO.OpaAnio=" + str(anio) + " AND OPAGO2.BENCUI=") + str(cuit)
        cursor.execute(sql_query)

        context = {
            'titulo': "OP Pagadas",
            'pagadas': cursor,
            'anio': anio,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

class op_pagadas_detalle(View):
    """ VISTA DE DETALLE DE ORDEN DE COMPRA """
    template_name = 'proveedores/op_pagadas_detalle.html'
    def get_context_data(self, **kwargs):

        OpaAnio = self.request.GET['OpaAnio']
        OpaNro = self.request.GET['OpaNro']
        jurcod = self.request.GET['jurcod']
        repudo = self.request.GET['repudo']

        conexion = conectarSQL()
        cursor = conexion.cursor(as_dict=True)

        sql_query = "SELECT * FROM OPAGO2 WHERE OpaAnio=" + str(OpaAnio) + " AND OpaNro=" + str(
            OpaNro) + " AND jurcod='" + str(jurcod) + "' AND repudo='" + str(repudo) + "'"
        cursor.execute(sql_query)
        cabecera = cursor.fetchone()

        sql_query = "SELECT * FROM OPAGO1 WHERE OpaAnio=" + str(OpaAnio) + " AND OpaNro=" + str(
            OpaNro) + " AND jurcod='" + str(jurcod) + "' AND repudo='" + str(repudo) + "'"
        cursor.execute(sql_query)
        detalle = cursor


        context = {
            'titulo': 'Detalle de la OP',
            'cabecera': cabecera,
            'detalle': detalle,

        }
        return context
    def get(self, request, *args, **kwargs):
        data = dict()
        data['html_form'] = render_to_string(self.template_name, self.get_context_data(), request=request)
        return JsonResponse(data)


class op_pagadas_comprobante(View):
    """ VISTA DE COMPROBANTE DE PAGO"""
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
    """ IMPRESOR DE OP """
    template_name = 'proveedores/op_pagadas_pdf.html'

    def get(self, request, *args, **kwargs):

        OpaAnio = kwargs['OpaAnio']
        OpaNro = kwargs['OpaNro']
        jurcod = kwargs['jurcod']
        repudo = kwargs['repudo']

        conexion = conectarSQL()
        cursor = conexion.cursor(as_dict=True)

        sql_query = "SELECT * FROM OPAGO2 WHERE OpaAnio=" + str(OpaAnio) + " AND OpaNro=" + str(
            OpaNro) + " AND jurcod='" + str(jurcod) + "' AND repudo='" + str(repudo) + "'"
        cursor.execute(sql_query)
        cabecera = cursor.fetchone()

        sql_query = "SELECT * FROM REPARTICI1 WHERE jurcod='" + str(jurcod) + "' AND repudo='" + str(repudo) + "'"
        cursor.execute(sql_query)
        reparticion = cursor.fetchone()

        sql_query = "SELECT * FROM OPAGO1 WHERE OpaAnio=" + str(OpaAnio) + " AND OpaNro=" + str(
            OpaNro) + " AND jurcod='" + str(jurcod) + "' AND repudo='" + str(repudo) + "'"
        cursor.execute(sql_query)
        detalle = cursor
       
        context = {
            'cabecera': cabecera,
            'detalle': detalle,
            'reparticion': reparticion,
            'importeTexto': decimal_a_texto(cabecera['Opapgd']),

        }
        
        return generate_pdf(request, self.template_name, context)


def decimal_a_texto(numero):
    """ FUNCION PARA CONVERTIR NUMEROS DECIMALES A TEXTO (se usa en importe) """
    parte_entera = int(numero)
    parte_decimal = int((numero - parte_entera) * 100)  # Multiplica por 100 y convierte a entero
    texto_entero = num2words(parte_entera, lang='es')
    texto_decimal = num2words(parte_decimal, lang='es')

    if parte_decimal > 0:
        return f"{texto_entero} punto {texto_decimal}"
    else:
        return texto_entero


def op_pagadas_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA """
    cuit = 30718402235

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    conexion = conectarSQL()
    cursor = conexion.cursor(as_dict=True)
    sql_query = ("SELECT * FROM POPAGO INNER JOIN OPAGO2 ON POPAGO.OpaAnio=OPAGO2.OpaAnio "
                 "AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod "
                 "AND POPAGO.repudo=OPAGO2.repudo WHERE OPAGO2.BENCUI=") + str(cuit)


    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        sql_query = sql_query + " AND POPAGO.OpaAnio=" + request.POST.get('ejer_ajax')
    # FILTRAR POR JURISDICCION
    if request.POST.get('jur_ajax'):
        sql_query = sql_query + " AND POPAGO.jurcod=" + request.POST.get('jur_ajax')
    # FILTRAR POR UNIDAD DE JURISDICCION
    if request.POST.get('udo_ajax'):
        sql_query = sql_query + " AND POPAGO.repudo=" + request.POST.get('udo_ajax')
    # FILTRAR POR UNIDAD NUMERO DE OP
    if request.POST.get('nro_op_ajax'):
        sql_query = sql_query + " AND POPAGO.OpaNro=" + request.POST.get('nro_op_ajax')
    # FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax'):
        sql_query = sql_query + " AND POPAGO.Popfpg>='" + request.POST.get('desde_ajax') + "'"
    # FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax'):
        sql_query = sql_query + " AND POPAGO.Popfpg<='" + request.POST.get('hasta_ajax') + "'"
    # FILTRAR POR TIPOS DE CHEQUES
    if request.POST.get('cheque_ajax'):
        #FALTA HACER
        sql_query = sql_query

    cursor.execute(sql_query)
    data = list(cursor)
    return JsonResponse(data, safe=False)