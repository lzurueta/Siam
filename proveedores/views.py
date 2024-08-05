from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from requests import Session

from sistema.models import Profile

from num2words import num2words

from proveedores.models import CPOPAGO
from sistema.functions import generate_pdf,generate_excel, conectarSQL

import datetime

from zeep import Client, Transport
import json

import requests
from django.conf import settings

class proveedoresHome(View):
    def get_context_data(self, **kwargs):
        cuit = self.request.user.username
        context = {
            'titulo': "Proveedores",
            'cuit': cuit
        }
        return context

    def get(self, request, *args, **kwargs):
        template_name = 'proveedores/index.html'
        return render(request, template_name, self.get_context_data())


class op_pagadas(View):
    template_name = 'proveedores/op_pagadas.html'

    def get_context_data(self, **kwargs):
        cuit = self.request.user.username
        anio = datetime.datetime.now().year

        context = {
            'titulo': "OP Pagadas",
            'anio': anio,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


def op_imprimir(request):
    """ IMPRESOR DE OP """
    template_name = 'proveedores/op_pagadas_pdf.html'

    OpaAnio = request.POST.get('ejercicio')
    OpaNro = request.POST.get('nroOP')
    jurcod = request.POST.get('juri')
    repudo = request.POST.get('udo')


    url = 'https://api.tujujuy.gob.ar/v1/proveedores/imprimircabeceraop/ejerchar='+ OpaAnio +'&nroOPchar='+ OpaNro +'&jurcod='+ jurcod +'&repudo='+repudo

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    cabecera = data['SDTOPCabecera'][0]

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/imprimirdetalleop/ejerchar='+ OpaAnio +'&nroOPchar='+ OpaNro +'&jurcod='+ jurcod +'&repudo='+repudo

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    detalle = data['SDTOPComprobantes']

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/totalizaop/opaanio=' + OpaAnio + '&OpaNro=' + OpaNro + '&jurcod=' + jurcod + '&repudo=' + repudo

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    total = data['total']

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/pagoasociado/opaanio=' + OpaAnio + '&OpaNro=' + OpaNro + '&jurcod=' + jurcod + '&repudo=' + repudo

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    pagosAsociados = data

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/totalizaactivoop/opaanio=' + OpaAnio + '&OpaNro=' + OpaNro + '&jurcod=' + jurcod + '&repudo=' + repudo

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    totalPagosAsoc = data['total']


    if total:
        totalAux = float(total)
    else:
        totalAux = 0

    if totalPagosAsoc:
        totalPagosAsocAux = float(totalPagosAsoc)
    else:
        totalPagosAsocAux = 0

    saldo = float(totalAux) - float(totalPagosAsocAux)

    print(totalPagosAsoc)

    context = {
            'cabecera': cabecera,
            'detalle': detalle,
            'importeTexto': decimal_a_texto(total),
            'importe': total,
            'pagosAsociados': pagosAsociados,
            'saldo': saldo

        }

    return generate_pdf(request, template_name, context)


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
    cuit = request.user.username

    ejer = ''
    jur = ''
    udo = ''
    nroOp = ''
    desde = ''
    hasta = ''

    #  FILTRAR POR EJE
    if request.POST.get('ejer_ajax') != '':
        ejer = '=' + request.POST.get('ejer_ajax')

    #  FILTRAR POR JUR
    if request.POST.get('jur_ajax') != '':
        jur = '=' + request.POST.get('jur_ajax')

    #  FILTRAR POR UDO
    if request.POST.get('udo_ajax') != '':
        udo = '=' + request.POST.get('udo_ajax')

    #  FILTRAR POR NRO OP
    if request.POST.get('nro_op_ajax') != '':
        nroOp = '=' + request.POST.get('nro_op_ajax')

    #  FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax') != '':
        desde = '=' + request.POST.get('desde_ajax')

    #  FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax') != '':
        hasta = '=' + request.POST.get('hasta_ajax')

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/OPPagadas/cuitchar='+cuit+'&ejerchar'+ejer+'&jur'+jur+'&udo='+udo+'&nroOPchar'+nroOp+'&FecDesde'+desde+'&FecHasta'+hasta

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    op_pagadas = data['SDTOPPagadasCuit']

    return JsonResponse(op_pagadas, safe=False)

def op_detalle(request):
    """ VISTA DE DETALLE DE ORDEN DE COMPRA """
    template_name = 'proveedores/op_detalle.html'

    if request.method == 'POST':

        OpaAnio = request.POST.get('OpaAnio')
        OpaNro = request.POST.get('OpaNro')
        jurcod = request.POST.get('jurcod')
        repudo = request.POST.get('repudo')

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/imprimircabeceraop/ejerchar='+OpaAnio+'&nroOPchar='+OpaNro+'&jurcod='+jurcod+'&repudo='+repudo

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        cabecera = data['SDTOPCabecera'][0]

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/imprimirdetalleop/ejerchar=' + OpaAnio + '&nroOPchar=' + OpaNro + '&jurcod=' + jurcod + '&repudo=' + repudo

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        detalle = data['SDTOPComprobantes']


        context = {
            'titulo': 'Detalle de la OP N° '+OpaNro,
            'cabecera': cabecera,
            'detalle': detalle

        }


        data = dict()
        data['html_form'] = render_to_string(template_name, context, request=request)
        return JsonResponse(data)

    else:
        # Si la solicitud no es POST, devolver un error
        respuesta = {'error': 'Solicitud no permitida'}
        return JsonResponse(respuesta, status=405)


def op_pagadas_retenciones(request):
    """ VISTA DE RETENCIONES DE ORDEN DE COMPRA """
    template_name = 'proveedores/op_pagadas_retenciones.html'
    cuit = request.user.username
    if request.method == 'POST':

        OpaAnio = request.POST.get('OpaAnio')
        OpaNro = request.POST.get('OpaNro')
        jurcod = request.POST.get('jurcod')
        repudo = request.POST.get('repudo')

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/imprimircabeceraop/ejerchar=' + OpaAnio + '&nroOPchar=' + OpaNro + '&jurcod=' + jurcod + '&repudo=' + repudo

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        cabecera = data['SDTOPCabecera'][0]

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/retencionesop/cuitchar=' + cuit + '&nroOPchar=' + OpaNro + '&opaaniochar=' +OpaAnio+ '&jurcod=' + jurcod + '&repudo=' + repudo

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        detalle = data['SDTRetencionesOP']

        context = {
            'titulo': 'Retenciones de la OP N° '+OpaNro,
            'cabecera': cabecera,
            "detalle": detalle

        }


        data = dict()
        data['html_form'] = render_to_string(template_name, context, request=request)
        return JsonResponse(data)

    else:
        # Si la solicitud no es POST, devolver un error
        respuesta = {'error': 'Solicitud no permitida'}
        return JsonResponse(respuesta, status=405)


def op_pagadas_comprobante(request):
    """ VISTA DE DETALLE DE ORDEN DE COMPRA """
    template_name = 'proveedores/op_pagadas_comprobante.html'

    if request.method == 'POST':
        OpaAnio = request.POST.get('OpaAnio')
        OpaNro = request.POST.get('OpaNro')
        jurcod = request.POST.get('jurcod')
        repudo = request.POST.get('repudo')
        popnro = request.POST.get('popnro')
        ejer = request.POST.get('ejer')


        url = 'https://api.tujujuy.gob.ar/v1/proveedores/cpbtedepago/opaaniochar='+ OpaAnio +'&popnrochar='+ popnro +'&ejerchar='+ ejer +'&opanrochar='+ OpaNro +'&jurcod='+ jurcod +'&repudo='+repudo

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        detalle = data['SDTCpbtePago'][0]


        context = {
        'titulo': 'Comprobante de pago - OP N° ' + OpaNro,
        'detalle': detalle
        }

        data = dict()
        data['html_form'] = render_to_string(template_name, context, request=request)
        return JsonResponse(data)

    else:
        respuesta = {'error': 'Solicitud no permitida'}
        return JsonResponse(respuesta, status=405)


def datos_proveedor(request):
    """ VISTA DE DATOS DE PROVEEDOR """
    template_name = 'proveedores/datos_proveedor.html'

    if request.method == 'POST':
        cuit = request.POST.get('cuit')

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/DatosProveedor/cuit='+cuit
        urlActividad = 'https://api.tujujuy.gob.ar/v1/proveedores/ActividadProveedor/cuit='+cuit

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        detalle = data['SdtDatosProveedor'][0]

        responseActividad = requests.get(urlActividad, headers=headers, verify=False)
        responseActividad.raise_for_status()
        dataActividad = responseActividad.json()
        actividad = dataActividad['SDTActividad']

        context = {
         'detalle': detalle,
         'actividad': actividad
        }

        data = dict()
        data['html_form'] = render_to_string(template_name, context, request=request)
        return JsonResponse(data)

    else:
        respuesta = {'error': 'Solicitud no permitida'}
        return JsonResponse(respuesta, status=405)


def datos_declaracion_jurada_imprimir(request):
    """ IMPRESOR DE DECLARACION JURADA """

    template_name = 'registration/declaracion_jurada_pdf.html'

    profile = Profile.objects.get(user=request.user)

    context = {
        'profile': profile
    }

    return generate_pdf(request, template_name, context)


class op_impagas(View):
    template_name = 'proveedores/op_impagas.html'

    def get_context_data(self, **kwargs):
        cuit = self.request.user.username
        anio = datetime.datetime.now().year


        context = {
            'titulo': "OP Impagas",
            'anio': anio,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


def op_impagas_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA """
    cuit = request.user.username

    ejer = ''
    jur=''
    udo = ''
    nroOPchar = ''
    opaest =''


    #  FILTRAR POR EJE
    if request.POST.get('ejer_ajax') != '':
       ejer = '='+request.POST.get('ejer_ajax')

    # FILTRAR POR JUR
    if request.POST.get('jur_ajax') != '':
        jur = '='+request.POST.get('jur_ajax')

    # FILTRAR POR UDO
    if request.POST.get('udo_ajax') != '':
        udo = '='+request.POST.get('udo_ajax')

    #  FILTRAR POR OP
    if request.POST.get('nro_op_ajax') != '':
        nroOPchar = '='+request.POST.get('nro_op_ajax')

    #  FILTRAR POR ESTADI
    if request.POST.get('estado_ajax') != '':
        opaest = '=' + request.POST.get('estado_ajax')


    url = 'https://api.tujujuy.gob.ar/v1/proveedores/OPImpagas/cuitchar='+cuit+'&ejerchar'+ejer+'&jur'+jur+'&udo'+udo+'&nroOPchar'+nroOPchar+'&opaest'+opaest
    print(url)

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    op_impagas = data['SDTOPImpagas']

    return JsonResponse(op_impagas, safe=False)


class op_comprobantes(View):
    template_name = 'proveedores/op_comprobantes.html'

    def get_context_data(self, **kwargs):
        cuit = self.request.user.username

        context = {
            'titulo': "Comprobantes",
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

def op_comprobantes_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA """
    cuit = request.user.username
    OpaCpbTip = ''
    letra = ''
    CpbSucCar = ''
    OpaCpbNroCar = ''

    #  FILTRAR POR TIPO
    if request.POST.get('tipo_ajax') != '':
        OpaCpbTip = '=' +request.POST.get('tipo_ajax')

    # FILTRAR POR LETRA
    if request.POST.get('letra_ajax') != '':
        letra = '=' + request.POST.get('letra_ajax')

    # FILTRAR POR SUCURSAL
    if request.POST.get('suc_ajax') != '':
        CpbSucCar = '=' + request.POST.get('suc_ajax')

    #  FILTRAR POR NUMERO
    if request.POST.get('nro_ajax') != '':
        OpaCpbNroCar = '=' + request.POST.get('nro_ajax')


    url = 'https://api.tujujuy.gob.ar/v1/proveedores/ConsultaComprobante/cuitchar='+ cuit +'&OpaCpbTip'+ OpaCpbTip +'&letra'+ letra +'&CpbSucCar'+CpbSucCar+'&OpaCpbNroCar'+OpaCpbNroCar

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    comprobante = data['SDTComprobanteCuit']

    return JsonResponse(comprobante, safe=False)


def op_pagadas_excel(request):
        """ EXPORTADOR A EXCEL DE OPs PAGADAS """
        template_name = 'proveedores/op_pagadas_excel.html'

        cuit = request.user.username
        #
        # conexion = conectarSQL()
        # cursor = conexion.cursor()
        #
        # if request.POST.get('tipo') == 'con':
        #  sql_query = (" SELECT  "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
        #     " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy') "
        #     " end as 'fecPago', "
        #     "CONCAT(POPAGO.OpaAnio,POPAGO.OpaNro,POPAGO.jurcod,POPAGO.repudo) as 'aux', "
        #     " POPAGO.OpaAnio as 'ejerOP', "
        #     " POPAGO.Popnro as 'nroLiq', "
        #     " POPAGO.OpaNro as 'nroOP', "
        #     " POPAGO.OpaAnio as 'ejerOP', "
        #     " POPAGO.jurcod as 'jur', "
        #     " POPAGO.repudo as 'udo', "
        #     " REPARTICIO.RepDes as 'reparticion', "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then 'Nota Debito' "
        #     " 	when POPAGO.Poptip='C' then 'Cheque' "
        #     " 	when POPAGO.Poptip='1' then 'Ingresos Brutos' "
        #     " 	when POPAGO.Poptip='4' then 'Ganancias' "
        #     " 	when POPAGO.Poptip='X' then 'Embargo' "
        #     " 	when POPAGO.Poptip='7' then 'Cesion' "
        #     " 	when POPAGO.Poptip='R' then 'DEPOSITO DE GARANTIA' "
        #     " 	when POPAGO.Poptip='S' then 'SEG.SOC.(I)' "
        #     " 	when POPAGO.Poptip='V' then 'C.JUJ.DE LA CONST.' "
        #     " 	when POPAGO.Poptip='Y' then 'IMP.A LOS SELLOS' "
        #     " 	when POPAGO.Poptip='L' then 'FONDO LABORATORIO - D.P.V.' "
        #     " 	when POPAGO.Poptip='«' then 'SEGURIDAD SOCIAL 6%' "
        #     " 	when POPAGO.Poptip='I' then 'LEY 5118/98 VIALIDAD' "
        #     " 	when POPAGO.Poptip='2' then 'MULTA' "
        #     " 	when POPAGO.Poptip='9' then 'F.B.JUJUY S.A. 260411/03' "
        #     " 	when POPAGO.Poptip='G' then 'LEY 5239/00 ART.33 D.G.ARQUITECTURA' "
        #     " 	when POPAGO.Poptip='U' then 'SEG.SOC.(C)' "
        #     " 	when POPAGO.Poptip='T' then 'LEY 5118' "
        #     " 	when POPAGO.Poptip='E' then 'RET EARPUJ DECR. 175-G-2012' "
        #     " 	when POPAGO.Poptip='_' then 'CONSTANCIAS DE DEUDA'	 "
        #     " end as 'formaPago',  "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then CONVERT(VARCHAR,POPAGO.Ndbnro) "
        #     " 	when POPAGO.Poptip='C' then CONVERT(VARCHAR,POPAGO.Chqnum)	 "
        #     " 	else 0 "
        #     " end as 'nroCpbtePago', "
        #     " POPAGO.Popimp as 'importe', "
        #     " OPAGO1.OpaCpbTip as 'tipoCbpte', "
        #     " OPAGO1.OpaCpbLet as 'letraCpbte', "
        #     " OPAGO1.OpaSu1 as 'sucursalCpbte', "
        #     " OPAGO1.OpaCpbNro as 'nroCpbte', "
        #     " format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte', "
        #     " OPAGO1.OpaImp as 'importeCpbte'	 "
        #     " from POPAGO  "
        #     " inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
        #     " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
        #     " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
        #     " inner join OPAGO1 on OPAGO1.OpaAnio=POPAGO.OpaAnio AND OPAGO1.OpaNro=POPAGO.OpaNro AND OPAGO1.jurcod=POPAGO.jurcod AND OPAGO1.repudo=POPAGO.repudo "
        #     " inner join BENEFICIAR on OPAGO1.CpbBenCUI=BENEFICIAR.BENCUI "
        #     " where OPAGO1.CpbBenCUI=" + str(cuit) + " AND POPAGO.PopEst<>'A' AND (POPAGO.Poptip='D' or POPAGO.Poptip='C') ")
        # else:
        #  sql_query = (" SELECT  "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
        #     " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy') "
        #     " end as 'fecPago', "
        #     " POPAGO.OpaAnio as 'ejerOP', "
        #     " POPAGO.Popnro as 'nroLiq', "
        #     " POPAGO.OpaNro as 'nroOP', "
        #     " POPAGO.OpaAnio as 'ejerOP', "
        #     " POPAGO.jurcod as 'jur', "
        #     " POPAGO.repudo as 'udo', "
        #     " REPARTICIO.RepDes as 'reparticion', "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then 'Nota Debito' "
        #     " 	when POPAGO.Poptip='C' then 'Cheque' "
        #     " 	when POPAGO.Poptip='1' then 'Ingresos Brutos' "
        #     " 	when POPAGO.Poptip='4' then 'Ganancias' "
        #     " 	when POPAGO.Poptip='X' then 'Embargo' "
        #     " 	when POPAGO.Poptip='7' then 'Cesion' "
        #     " 	when POPAGO.Poptip='R' then 'DEPOSITO DE GARANTIA' "
        #     " 	when POPAGO.Poptip='S' then 'SEG.SOC.(I)' "
        #     " 	when POPAGO.Poptip='V' then 'C.JUJ.DE LA CONST.' "
        #     " 	when POPAGO.Poptip='Y' then 'IMP.A LOS SELLOS' "
        #     " 	when POPAGO.Poptip='L' then 'FONDO LABORATORIO - D.P.V.' "
        #     " 	when POPAGO.Poptip='«' then 'SEGURIDAD SOCIAL 6%' "
        #     " 	when POPAGO.Poptip='I' then 'LEY 5118/98 VIALIDAD' "
        #     " 	when POPAGO.Poptip='2' then 'MULTA' "
        #     " 	when POPAGO.Poptip='9' then 'F.B.JUJUY S.A. 260411/03' "
        #     " 	when POPAGO.Poptip='G' then 'LEY 5239/00 ART.33 D.G.ARQUITECTURA' "
        #     " 	when POPAGO.Poptip='U' then 'SEG.SOC.(C)' "
        #     " 	when POPAGO.Poptip='T' then 'LEY 5118' "
        #     " 	when POPAGO.Poptip='E' then 'RET EARPUJ DECR. 175-G-2012' "
        #     " 	when POPAGO.Poptip='_' then 'CONSTANCIAS DE DEUDA' "
        #     " end as 'formaPago',  "
        #     " case  "
        #     " 	when POPAGO.Poptip='D' then CONVERT(VARCHAR,POPAGO.Ndbnro) "
        #     " 	when POPAGO.Poptip='C' then CONVERT(VARCHAR,POPAGO.Chqnum)		 "
        #     " 	else 0 "
        #     " end as 'nroCpbtePago', "
        #     " POPAGO.Popimp as 'importe' "
        #     " from POPAGO  "
        #     " inner join OPAGO2 on POPAGO.OpaAnio=OPAGO2.OpaAnio AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod AND POPAGO.repudo=OPAGO2.repudo "
        #     " inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
        #     " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
        #     " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
        #     " WHERE OPAGO2.BENCUI=" + str(cuit) + " AND POPAGO.PopEst<>'A' AND (POPAGO.Poptip='D' or POPAGO.Poptip='C') ")
        #
        #
        # # FILTRAR POR EJERCICIO
        # if request.POST.get('ejer_ajax'):
        #     sql_query = sql_query + " AND POPAGO.OpaAnio=" + request.POST.get('ejer_ajax')
        # # FILTRAR POR JURISDICCION
        # if request.POST.get('jur_ajax'):
        #     sql_query = sql_query + " AND POPAGO.jurcod=" + request.POST.get('jur_ajax')
        # # FILTRAR POR UNIDAD DE JURISDICCION
        # if request.POST.get('udo_ajax'):
        #     sql_query = sql_query + " AND POPAGO.repudo=" + request.POST.get('udo_ajax')
        # # FILTRAR POR NRO DE OP
        # if request.POST.get('nro_op_ajax'):
        #     sql_query = sql_query + " AND POPAGO.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
        # # FILTRAR POR FECHA DESDE
        # if request.POST.get('desde_ajax'):
        #     sql_query = sql_query + " AND POPAGO.Popfpg>='" + request.POST.get('desde_ajax') + "'"
        # # FILTRAR POR FECHA HASTA
        # if request.POST.get('hasta_ajax'):
        #     sql_query = sql_query + " AND POPAGO.Popfpg<='" + request.POST.get('hasta_ajax') + "'"
        #
        # cursor.execute(sql_query)
        # comprobante = cursor.fetchall()

        ejer = ''
        jur = ''
        udo = ''
        nroOp = ''
        desde = ''
        hasta = ''

        #  FILTRAR POR EJE
        if request.POST.get('ejer_ajax') != '':
            ejer = '=' + request.POST.get('ejer_ajax')

        #  FILTRAR POR JUR
        if request.POST.get('jur_ajax') != '':
            jur = '=' + request.POST.get('jur_ajax')

        #  FILTRAR POR UDO
        if request.POST.get('udo_ajax') != '':
            udo = '=' + request.POST.get('udo_ajax')

        #  FILTRAR POR NRO OP
        if request.POST.get('nro_op_ajax') != '':
            nroOp = '=' + request.POST.get('nro_op_ajax')

        #  FILTRAR POR FECHA DESDE
        if request.POST.get('desde_ajax') != '':
            desde = '=' + request.POST.get('desde_ajax')

        #  FILTRAR POR FECHA HASTA
        if request.POST.get('hasta_ajax') != '':
            hasta = '=' + request.POST.get('hasta_ajax')

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/OPPagadas/cuitchar=' + cuit + '&ejerchar' + ejer + '&jur' + jur + '&udo=' + udo + '&nroOPchar' + nroOp + '&FecDesde' + desde + '&FecHasta' + hasta

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        comprobante = data['SDTOPPagadasCuit']

        context = {
            "comprobante": comprobante,
            "tipo" : request.POST.get('tipo')
        }

        return generate_excel(request, template_name, context)


def op_impagas_excel(request):
    """ EXPORTADOR A EXCLE DE OPs IMPAGAS """
    template_name = 'proveedores/op_impagas_excel.html'

    cuit = request.user.username

    # conexion = conectarSQL()
    # cursor = conexion.cursor()
    #
    # if request.POST.get('tipo') == 'con':
    #   sql_query = (" SELECT  "
    #   " OPAGO2.OpaAnio as 'ejerOP', "
    #   " OPAGO2.OpaNro as 'nroOP', "
    #   " OPAGO2.jurcod as 'jur', "
    #   " OPAGO2.repudo as 'udo', "
    #   " format( OPAGO2.OpaEmi ,'dd/MM/yyyy') as 'fecEmi', "
    #   " REPARTICIO.RepDes as 'reparticion', "
    #   " OPAGO1.OpaCpbTip as 'tipoCbpte', "
    #   " OPAGO1.OpaCpbLet as 'letraCpbte', "
    #   " OPAGO1.OpaSu1 as 'sucursalCpbte', "
    #   " OPAGO1.OpaCpbNro as 'nroCpbte', "
    #   " (select  "
    #   " sum(opago1.opaimp)  "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND  "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo "
    #   " ) as 'ImporteTotalOP', "
    #   " opago2.opapgd as 'pagado', "
    #   " (select  "
    #   " sum(opago1.opaimp)  "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND  "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) - opago2.opapgd as 'SaldoOP', "
    #   " format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte', "
    #   " OPAGO1.OpaImp as 'importeCpbte', "
    #   " OPAGO2.OpaEst as 'habilitaContad', "
    #   " OPAGO2.OpaHaT as 'habilitaTeso' "
    #   " from OPAGO2  "
    #   " inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
    #   " inner join OPAGO1 on OPAGO1.OpaAnio=OPAGO2.OpaAnio AND OPAGO1.OpaNro=OPAGO2.OpaNro AND OPAGO1.jurcod=OPAGO2.jurcod AND OPAGO1.repudo=OPAGO2.repudo "
    #   " inner join BENEFICIAR on OPAGO1.CpbBenCUI=BENEFICIAR.BENCUI "
    #   " where OPAGO1.CpbBenCUI="+  str(cuit) +"  AND (select "
    #   " sum(OPAGO1.opaimp) "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) > OPAGO2.Opapgd  AND OPAGO2.OpaEst<>'A' ")
    # else:
    #     sql_query = ("SELECT  "
    #   " OPAGO2.OpaAnio as 'ejerOP', "
    #   " OPAGO2.OpaNro as 'nroOP', "
    #   " OPAGO2.jurcod as 'jur', "
    #   " JURISDICCI.JurDes as 'jurisdiccion', "
    #   " OPAGO2.repudo as 'udo', "
    #   " REPARTICIO.RepDes as 'reparticion', "
    #   " format( OPAGO2.OpaEmi ,'dd/MM/yyyy') as 'fecEmi', "
    #   " OPAGO2.OpaEst as 'estadoOPC', "
    #   " OPAGO2.OpaHaT as 'estadoOPT', "
    #   " OPAGO2.Opapgd as 'pagado', "
    #   " (select "
    #   " sum(OPAGO1.opaimp) "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) as 'ImporteTotalOP', "
    #   "((select "
    #   " sum(OPAGO1.opaimp) "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) - OPAGO2.Opapgd) as 'SaldoOP', "
    #   " OPAGO2.OpaEst as 'habilitaContad', "
    #   " OPAGO2.OpaHaT as 'habilitaTeso' "
    #   " from OPAGO2 "
    #   " inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
    #   " inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
    #   " inner join JURISDICCI on OPAGO2.jurcod=JURISDICCI.jurcod "
    #   "where opaest <> 'A' AND OPAGO2.BENCUI= " + str(cuit) + "  AND (select "
    #   " sum(OPAGO1.opaimp) "
    #   " from OPAGO1 "
    #   " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
    #   " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) > OPAGO2.Opapgd ")
    #
    # # FILTRAR POR EJERCICIO
    # if request.POST.get('ejer_ajax'):
    #     sql_query = sql_query + " AND OPAGO2.OpaAnio=" + request.POST.get('ejer_ajax')
    # # FILTRAR POR JURISDICCION
    # if request.POST.get('jur_ajax'):
    #     sql_query = sql_query + " AND POPAGO2.jurcod=" + request.POST.get('jur_ajax')
    # # FILTRAR POR UNIDAD DE JURISDICCION
    # if request.POST.get('udo_ajax'):
    #     sql_query = sql_query + " AND POPAGO2.repudo=" + request.POST.get('udo_ajax')
    # # FILTRAR POR NRO DE OP
    # if request.POST.get('nro_op_ajax'):
    #     sql_query = sql_query + " AND POPAGO2.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
    # # FILTRAR POR ESTADO
    # if request.POST.get('estado_ajax') != 'T':
    #     if request.POST.get('estado_ajax') == 'S':
    #      sql_query = sql_query + " AND OPAGO2.OpaEst IN ('S','H') "
    #     else:
    #         sql_query = sql_query + " AND OPAGO2.OpaEst is null "
    #
    # cursor.execute(sql_query)
    # comprobante = cursor.fetchall()

    ejer = ''
    jur = ''
    udo = ''
    nroOPchar = ''
    opaest = ''

    #  FILTRAR POR EJE
    if request.POST.get('ejer_ajax') != '':
        ejer = '=' + request.POST.get('ejer_ajax')

    # FILTRAR POR JUR
    if request.POST.get('jur_ajax') != '':
        jur = '=' + request.POST.get('jur_ajax')

    # FILTRAR POR UDO
    if request.POST.get('udo_ajax') != '':
        udo = '=' + request.POST.get('udo_ajax')

    #  FILTRAR POR OP
    if request.POST.get('nro_op_ajax') != '':
        nroOPchar = '=' + request.POST.get('nro_op_ajax')

    #  FILTRAR POR ESTADI
    if request.POST.get('estado_ajax') != '':
        opaest = '=' + request.POST.get('estado_ajax')

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/OPImpagas/cuitchar=' + cuit + '&ejerchar' + ejer + '&jur' + jur + '&udo' + udo + '&nroOPchar' + nroOPchar + '&opaest' + opaest
    print(url)

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    comprobante = data['SDTOPImpagas']


    context = {
        "comprobante": comprobante,
        "tipo": request.POST.get('tipo')
    }

    return generate_excel(request, template_name, context)

class op_retenciones(View):
    """ABRIR PAGINA DE RETNECIONES"""
    template_name = 'proveedores/op_retenciones.html'

    def get_context_data(self, **kwargs):
        cuit = self.request.user.username

        context = {
            'titulo': "Retenciones",
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

def op_retenciones_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA """
    cuit = request.user.username
    ejer = ''
    tipo = ''
    desde = ''
    hasta = ''

    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        ejer = '=' + request.POST.get('ejer_ajax')

    # FILTRAR POR TIPO
    if request.POST.get('tipo_ajax'):
        tipo = '=' + request.POST.get('tipo_ajax')

    # FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax'):
        desde = '=' + request.POST.get('desde_ajax')

    # FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax'):
        hasta = '=' + request.POST.get('hasta_ajax')

    url = 'https://api.tujujuy.gob.ar/v1/proveedores/retenciones/cuitchar=' + cuit +'&ejerchar' +ejer+ '&codretChar'+ tipo +'&opaaniochar&nroOPchar&jurcod&repudo&FecDesde'+ desde +'&FecHasta'+ hasta

    headers = {
        'Authorization': f'Bearer {settings.TOKEN_API}'
    }

    response = requests.get(url, headers=headers, verify=False)

    response.raise_for_status()
    data = response.json()
    retenciones = data['SDTRetencionesCuit']

    return JsonResponse(retenciones, safe=False)



def op_retenciones_pdf(request):
    """ IMPRESOR DE RETENCIONES """
    template_name = 'proveedores/op_retenciones_pdf.html'
    cuit = request.user.username
    tipo = request.POST.get('tipo')
    anio = request.POST.get('anio')
    cons = request.POST.get('cons')
    importe = request.POST.get('importe')

    if tipo == '4':

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/constanciagan/cuitchar=' + cuit + '&nroConstanciachar=' + cons + '&ejerchar=' + anio

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()

        comprobante = data['SDTConstanciaGan']
        cabecera = data['SDTConstanciaGan'][0]

    elif tipo == '1':

      url = 'https://api.tujujuy.gob.ar/v1/proveedores/constanciaib/cuitchar='+ cuit +'&nroConstanciachar='+ cons +'&ejerchar=' + anio

      headers = {
          'Authorization': f'Bearer {settings.TOKEN_API}'
      }

      response = requests.get(url, headers=headers, verify=False)

      response.raise_for_status()
      data = response.json()

      comprobante = data['SDTConstanciaIB']
      cabecera = data['SDTConstanciaIB'][0]

    else:

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/constanciaotros/cuitchar=' + cuit + '&nroConstanciachar=' + cons + '&ejerchar=' + anio

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()

        comprobante = data['SDTConstanciaOtros']
        cabecera = data['SDTConstanciaOtros'][0]

    context = {
        'tipo': tipo,
        'comprobante': comprobante,
        'cabecera': cabecera
    }

    return generate_pdf(request, template_name, context)

def op_retenciones_excel(request):
        """ EXPORTADOR A EXCEL DE RETENCIONES """
        template_name = 'proveedores/op_retenciones_excel.html'

        cuit = request.user.username
        ejer = ''
        tipo = ''
        desde = ''
        hasta = ''

        # FILTRAR POR EJERCICIO
        if request.POST.get('ejer_ajax'):
            ejer = '=' + request.POST.get('ejer_ajax')

        # FILTRAR POR TIPO
        if request.POST.get('tipo_ajax'):
            tipo = '=' + request.POST.get('tipo_ajax')

        # FILTRAR POR FECHA DESDE
        if request.POST.get('desde_ajax'):
            desde = '=' + request.POST.get('desde_ajax')

        # FILTRAR POR FECHA HASTA
        if request.POST.get('hasta_ajax'):
            hasta = '=' + request.POST.get('hasta_ajax')

        url = 'https://api.tujujuy.gob.ar/v1/proveedores/retenciones/cuitchar=' + cuit + '&ejerchar' + ejer + '&codretChar' + tipo + '&opaaniochar&nroOPchar&jurcod&repudo&FecDesde' + desde + '&FecHasta' + hasta

        headers = {
            'Authorization': f'Bearer {settings.TOKEN_API}'
        }

        response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        data = response.json()
        datos = data['SDTRetencionesCuit']

        context = {
            "datos": datos,
        }

        return generate_excel(request, template_name, context)



def consultar_estado(request):
    """ TRAER DATOS DE CEDULA FISCAL """

    cuit = request.user.username
    template_name = 'proveedores/op_proveedores_cedulas.html'
    session = Session()
    session.verify = False
    transport = Transport(session=session)
    client = Client('https://www.rentasjujuyonline.gob.ar/consultacuit/ConsultaConstancia.asmx?WSDL', transport=transport)
    client.transport.session.verify = False

    # Realizar la llamada al método "Estado" del servicio con el parámetro cuit
    response = client.service.Estado(cuit=cuit)
    
    if response != 'No existen datos':

        data = json.loads(response)

        numero = data['Numero']
        anio = data['Anio']
        fecha_vigencia = data['FechaVigencia']
        nombre = data['Nombre']
        estado = data['Estado']
        tipo = data['Tipo']
        resultado = 'con'
    else:

        numero = ''
        anio = ''
        fecha_vigencia = ''
        nombre = ''
        estado = ''
        tipo = ''
        resultado = 'sin'

    context =  {

        'numero' : numero,
        'anio' : anio,
        'fecha_vigencia' :  fecha_vigencia,
        'nombre' : nombre,
        'estado' : estado,
        'tipo' : tipo,
        'resultado' : resultado
    }

    data = dict()
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

class historial_pagos(View):
    template_name = 'proveedores/historial_pagos.html'

    def get_context_data(self, **kwargs):
        cuit = self.request.user.username
        anio = datetime.datetime.now().year

        context = {
            'titulo': "Historial de Pagos",
            'anio': anio,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

