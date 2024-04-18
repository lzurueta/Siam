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

# Create your views here.
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



    conexion = conectarSQL()
    cursor = conexion.cursor()

    sql_query = ("SELECT OPAGO2.OpaAnio as 'ejercicio',"
                     "OPAGO2.OpaNro as 'nroOP',"
                     "JURISDICCI.JurDes, "
                     "REPARTICIO.RepDes as 'reparticion',"
                     " OPAGO2.OpaLug as 'lugar',"
                     "format(OPAGO2.OpaEmi,'dd/MM/yyyy') as 'fecEmision',"
                     " BENEFICIAR.BenNom as 'nombreProveedor',"
                     " OPAGO2.BENCUI as 'cuit',"
                     " OPAGO2.OpaNom as 'paguese',"
                     "OPAGO2.jurcod,"
                     "OPAGO2.repudo"
                     " FROM OPAGO2 "
                     "inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
                     "inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
                     "inner join JURISDICCI on OPAGO2.jurcod=JURISDICCI.jurcod "
                     "where OPAGO2.OpaAnio="+ str(OpaAnio) +" AND OPAGO2.OpaNro="+ str(OpaNro) +" AND OPAGO2.jurcod='"+ str(jurcod) +"' and OPAGO2.repudo='"+ str(repudo) +"'")

    cursor.execute(sql_query)
    cabecera = cursor.fetchone()

    sql_query = ("SELECT "
                     "CPBTES3.OcpNro as 'nroOrdCompra',"
                     "CPBTES3.OcpAnio as 'anioOrdCompra',"
                     "MOVIMIE1.nomp1 as 'partidaN1',"
                     "MOVIMIE1.nomp2 as 'partidaN2',"
                     "MOVIMIE1.nomp3 as 'partidaN3',"
                     "MOVIMIE1.nomp4 as 'partidaN4',"
                     "NOMENCLADO.NomDes as 'partidaNombre',"
                     "case "
                     "	when MOVIMIE1.MOVEXPTIP='EE' then MOVIMIE1.MOVEXPGD"
                     "	else concat(rtrim(MOVIMIE1.MovexpL),'-', MOVIMIE1.MovExpN,'/', MOVIMIE1.MovExpA)"
                     "end as 'expediente',"
                     "OPAGO1.OpaCpbTip as 'tipoCbpte',"
                     "OPAGO1.OpaCpbLet as 'letraCpbte',"
                     "OPAGO1.OpaSu1 as 'sucursalCpbte',"
                     "OPAGO1.OpaCpbNro as 'nroCpbte',"
                     "format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte',"
                     "OPAGO1.OpaImp as 'importeCpbte'"
                     "from OPAGO1"
                     " INNER join OPAGO2 on OPAGO1.OpaAnio=OPAGO2.OpaAnio AND OPAGO1.OpaNro=OPAGO2.OpaNro AND OPAGO1.jurcod=OPAGO2.jurcod AND OPAGO1.repudo=OPAGO2.repudo"
                     " INNER join CPBTES3 on OPAGO1.CpbBenCUI=CPBTES3.BENCUI AND OPAGO1.OpaCpbLet=CPBTES3.CpbLet AND OPAGO1.OpaCpbTip=CPBTES3.CpbTip AND OPAGO1.OpaSu1=CPBTES3.CpbSu1 AND OPAGO1.OpaCpbNro=CPBTES3.CpbNro"
                     " INNER join OCPRA3 on CPBTES3.OcpAnio=OCPRA3.OcpAnio and CPBTES3.OcpNro=OCPRA3.OcpNro and CPBTES3.jurcod=OCPRA3.jurcod and CPBTES3.repudo=OCPRA3.repudo"
                     " INNER join MOVIMIE1 on MOVIMIE1.MovAnio=OCPRA3.MovAnio and MOVIMIE1.MovCod=OCPRA3.MovCod and MOVIMIE1.jurcod=OCPRA3.jurcod and MOVIMIE1.repudo=OCPRA3.repudo"
                     " INNER join NOMENCLADO on MOVIMIE1.nomp1=NOMENCLADO.nomp1 and MOVIMIE1.nomp2=NOMENCLADO.nomp2 and MOVIMIE1.nomp3=NOMENCLADO.nomp3 and MOVIMIE1.nomp4=NOMENCLADO.nomp4  and MOVIMIE1.scccod=NOMENCLADO.scccod and MOVIMIE1.sctcod=NOMENCLADO.sctcod "
                     " WHERE OPAGO2.OpaAnio="+ str(OpaAnio) +" AND OPAGO2.OpaNro="+ str(OpaNro) +" AND OPAGO2.jurcod='"+ str(jurcod) +"' and OPAGO2.repudo='"+ str(repudo) +"'")

    cursor.execute(sql_query)
    detalle = cursor.fetchall()

    sql_query = ("SELECT "
                     "SUM(OPAGO1.OpaImp) as 'importeCpbte' "
                     "from OPAGO1"
                     " INNER join OPAGO2 on OPAGO1.OpaAnio=OPAGO2.OpaAnio AND OPAGO1.OpaNro=OPAGO2.OpaNro AND OPAGO1.jurcod=OPAGO2.jurcod AND OPAGO1.repudo=OPAGO2.repudo"
                     " WHERE OPAGO2.OpaAnio=" + str(OpaAnio) + " AND OPAGO2.OpaNro=" + str(OpaNro) + " AND OPAGO2.jurcod='" + str(jurcod) + "' and OPAGO2.repudo='" + str(repudo) + "'"
                     " GROUP BY OPAGO2.OpaAnio,OPAGO2.OpaNro,OPAGO2.jurcod,OPAGO2.repudo")

    cursor.execute(sql_query)
    total = cursor.fetchone()

    sql_query = (" SELECT  "
                    " POPAGO.Popnro as 'nroLiq',  "
                    " case  "
                    " 	when POPAGO.Poptip='D' then 'NOTA DÉBITO' "
                    " 	when POPAGO.Poptip='C' then 'CHEQUE' "
                    " 	when POPAGO.Poptip='1' then 'INGRESOS BRUTOS' "
                    " 	when POPAGO.Poptip='4' then 'GANANCIAS' "
                    " 	when POPAGO.Poptip='X' then 'EMBARGO' "
                    " 	when POPAGO.Poptip='7' then 'CESIÓN' "
                    " 	when POPAGO.Poptip='R' then 'DEPOSITO DE GARANTIA' "
                    " 	when POPAGO.Poptip='S' then 'SEG.SOC.(I)' "
                    " 	when POPAGO.Poptip='V' then 'C.JUJ.DE LA CONST.' "
                    " 	when POPAGO.Poptip='Y' then 'IMP.A LOS SELLOS' "
                    " 	when POPAGO.Poptip='L' then 'FONDO LABORATORIO - D.P.V.' "
                    " 	when POPAGO.Poptip='«' then 'SEGURIDAD SOCIAL 6%' "
                    " 	when POPAGO.Poptip='I' then 'LEY 5118/98 VIALIDAD' "
                    " 	when POPAGO.Poptip='2' then 'MULTA' "
                    " 	when POPAGO.Poptip='9' then 'F.B.JUJUY S.A. 260411/03' "
                    " 	when POPAGO.Poptip='G' then 'LEY 5239/00 ART.33 D.G.ARQUITECTURA' "
                    " 	when POPAGO.Poptip='U' then 'SEG.SOC.(C)' "
                    " 	when POPAGO.Poptip='T' then 'LEY 5118' "
                    " 	when POPAGO.Poptip='E' then 'RET EARPUJ DECR. 175-G-2012' "
                    " 	when POPAGO.Poptip='_' then 'CONSTANCIAS DE DEUDA'	 "
                    " end as 'tipoPago', " 
                    " case  "
                    " 	when POPAGO.Poptip='D' then CONCAT(CONVERT(VARCHAR,POPAGO.Ndbnro),'/', CONVERT(VARCHAR,POPAGO.NdbAnio))	 "
                    " 	when POPAGO.Poptip='C' then CONVERT(VARCHAR, POPAGO.Chqnum) "
                    "   else '0' "
                    " end as 'cpbtePago', "
                    " format(POPAGO.Popfpg,'dd/MM/yyyyy') as 'fecAplic', "
                    " case  "
                    " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
                    " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy') "
                    " end as 'fecPago', "
                    " POPAGO.Popimp as 'importeLiq' "
                    " FROM POPAGO  "
                    " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
                    " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
                    " where POPAGO.popEst <> 'A' AND POPAGO.OpaAnio="+ str(OpaAnio) +" AND POPAGO.OpaNro="+ str(OpaNro) +" AND POPAGO.jurcod='"+ str(jurcod) +"' AND POPAGO.repudo='"+ str(repudo) +"' ")

    cursor.execute(sql_query)
    pagosAsociados = cursor.fetchall()

    sql_query = (" SELECT "
                     " SUM(POPAGO.Popimp) as 'total' "
                     " FROM POPAGO  "
                     " where POPAGO.popEst <> 'A' AND POPAGO.OpaAnio=" + str(OpaAnio) + " AND POPAGO.OpaNro=" + str(OpaNro) + " AND POPAGO.jurcod='" + str(jurcod) + "' AND POPAGO.repudo='" + str(repudo) + "' "
                     " GROUP BY POPAGO.OpaAnio,POPAGO.OpaNro,POPAGO.jurcod,POPAGO.repudo ")

    cursor.execute(sql_query)
    totalPagosAsoc = cursor.fetchone()

    if total:
        totalAux = float(total[0])
    else:
        totalAux = 0

    if totalPagosAsoc:
        totalPagosAsocAux = float(totalPagosAsoc[0])
    else:
        totalPagosAsocAux = 0

    saldo = float(totalAux) - float(totalPagosAsocAux)

    context = {
            'cabecera': cabecera,
            'detalle': detalle,
            'importeTexto': decimal_a_texto(total[0]),
            'importe': total[0],
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

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    conexion = conectarSQL()
    cursor = conexion.cursor()
    sql_query = ("SELECT "
    "POPAGO.OpaAnio as 'ejercicio', "
    "POPAGO.OpaNro as 'nroOP',"
    "POPAGO.jurcod as 'juri',"
    "POPAGO.repudo as 'udo',"
    "POPAGO.Poptip as 'estadoPago',"
    "case "
    "	when POPAGO.Poptip='D' then 'Acreditación'"
    "	when POPAGO.Poptip='C' then 'Cheque'"
    "end as 'tipoPago', "
    "POPAGO.Popimp,"
    "case "
    "	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')"
    "	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy')"
    "end as 'fecPago',"
    "POPAGO.Popimp as 'importepago', "
    "OPAGO2.Opapgd as 'pagado',"
    "REPARTICIO.RepDes as 'reparticion',"
    "OPAGO2.BENCUI as 'cuit', "
    "POPAGO.Popnro as 'popnro' "
    "from POPAGO "
    "inner join OPAGO2 on POPAGO.OpaAnio=OPAGO2.OpaAnio AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod AND POPAGO.repudo=OPAGO2.repudo "
    "left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
    "left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
    "inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
    "where OPAGO2.BENCUI="+cuit+" and POPAGO.PopEst<>'A' AND (POPAGO.Poptip='D' or POPAGO.Poptip='C') ")


    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        sql_query = sql_query + " AND POPAGO.OpaAnio='" + request.POST.get('ejer_ajax') + "'"
    # FILTRAR POR JURISDICCION
    if request.POST.get('jur_ajax'):
        sql_query = sql_query + " AND POPAGO.jurcod='" + request.POST.get('jur_ajax') + "'"
    # FILTRAR POR UNIDAD DE JURISDICCION
    if request.POST.get('udo_ajax'):
        sql_query = sql_query + " AND POPAGO.repudo='" + request.POST.get('udo_ajax') + "'"
    # FILTRAR POR NRO DE OP
    if request.POST.get('nro_op_ajax'):
       sql_query = sql_query + " AND POPAGO.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
    # FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax'):
        sql_query = sql_query + " AND POPAGO.Popfpg>='" + request.POST.get('desde_ajax') + "'"
    # FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax'):
        sql_query = sql_query + " AND POPAGO.Popfpg<='" + request.POST.get('hasta_ajax') + "'"


    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)


def op_detalle(request):
    """ VISTA DE DETALLE DE ORDEN DE COMPRA """
    template_name = 'proveedores/op_detalle.html'

    if request.method == 'POST':

        OpaAnio = request.POST.get('OpaAnio')
        OpaNro = request.POST.get('OpaNro')
        jurcod = request.POST.get('jurcod')
        repudo = request.POST.get('repudo')

        conexion = conectarSQL()
        cursor = conexion.cursor()

        sql_query = ("SELECT OPAGO2.OpaAnio as 'ejercicio',"
                     "OPAGO2.OpaNro as 'nroOP',"
                     "OPAGO2.jurcod, "
                     "OPAGO2.repudo,"
                     " OPAGO2.OpaLug as 'lugar',"
                     "format(OPAGO2.OpaEmi,'dd/MM/yyyy') as 'fecEmision',"
                     " BENEFICIAR.BenNom as 'nombreProveedor',"
                     " OPAGO2.BENCUI as 'cuit',"
                     " OPAGO2.OpaNom as 'paguese'"
                     " FROM OPAGO2 "
                     "inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
                     "where OPAGO2.OpaAnio=" + str(OpaAnio) + " AND OPAGO2.OpaNro=" + str(OpaNro) + " AND OPAGO2.jurcod='" + str(jurcod) + "' and OPAGO2.repudo='" + str(repudo) + "'")

        cursor.execute(sql_query)
        cabecera = cursor.fetchone()


        sql_query = ("SELECT "
                     "CPBTES3.OcpNro as 'nroOrdCompra',"
                     "CPBTES3.OcpAnio as 'anioOrdCompra',"
                     "MOVIMIE1.nomp1 as 'partidaN1',"
                     "MOVIMIE1.nomp2 as 'partidaN2',"
                     "MOVIMIE1.nomp3 as 'partidaN3',"
                     "MOVIMIE1.nomp4 as 'partidaN4',"
                     "NOMENCLADO.NomDes as 'partidaNombre',"
                     "case "
                     "	when MOVIMIE1.MOVEXPTIP='EE' then MOVIMIE1.MOVEXPGD"
                     "	else concat(rtrim(MOVIMIE1.MovexpL),'-', MOVIMIE1.MovExpN,'/', MOVIMIE1.MovExpA)"
                     "end as 'expediente',"
                     "OPAGO1.OpaCpbTip as 'tipoCbpte',"
                     "OPAGO1.OpaCpbLet as 'letraCpbte',"
                     "OPAGO1.OpaSu1 as 'sucursalCpbte',"
                     "OPAGO1.OpaCpbNro as 'nroCpbte',"
                     "format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte',"
                     "OPAGO1.OpaImp as 'importeCpbte'"
                     "from OPAGO1"
                     " INNER join OPAGO2 on OPAGO1.OpaAnio=OPAGO2.OpaAnio AND OPAGO1.OpaNro=OPAGO2.OpaNro AND OPAGO1.jurcod=OPAGO2.jurcod AND OPAGO1.repudo=OPAGO2.repudo"
                     " INNER join CPBTES3 on OPAGO1.CpbBenCUI=CPBTES3.BENCUI AND OPAGO1.OpaCpbLet=CPBTES3.CpbLet AND OPAGO1.OpaCpbTip=CPBTES3.CpbTip AND OPAGO1.OpaSu1=CPBTES3.CpbSu1 AND OPAGO1.OpaCpbNro=CPBTES3.CpbNro"
                     " INNER join OCPRA3 on CPBTES3.OcpAnio=OCPRA3.OcpAnio and CPBTES3.OcpNro=OCPRA3.OcpNro and CPBTES3.jurcod=OCPRA3.jurcod and CPBTES3.repudo=OCPRA3.repudo"
                     " INNER join MOVIMIE1 on MOVIMIE1.MovAnio=OCPRA3.MovAnio and MOVIMIE1.MovCod=OCPRA3.MovCod and MOVIMIE1.jurcod=OCPRA3.jurcod and MOVIMIE1.repudo=OCPRA3.repudo"
                     " INNER join NOMENCLADO on MOVIMIE1.nomp1=NOMENCLADO.nomp1 and MOVIMIE1.nomp2=NOMENCLADO.nomp2 and MOVIMIE1.nomp3=NOMENCLADO.nomp3 and MOVIMIE1.nomp4=NOMENCLADO.nomp4  and MOVIMIE1.scccod=NOMENCLADO.scccod and MOVIMIE1.sctcod=NOMENCLADO.sctcod "
                     " WHERE OPAGO2.OpaAnio="+ str(OpaAnio) +" AND OPAGO2.OpaNro="+ str(OpaNro) +" AND OPAGO2.jurcod='"+ str(jurcod) +"' and OPAGO2.repudo='"+ str(repudo) +"'")

        cursor.execute(sql_query)
        detalle = cursor.fetchall()

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

        conexion = conectarSQL()
        cursor = conexion.cursor()

        sql_query = ("SELECT OPAGO2.OpaAnio as 'ejercicio',"
                     "OPAGO2.OpaNro as 'nroOP',"
                     "OPAGO2.jurcod, "
                     "OPAGO2.repudo,"
                     " OPAGO2.OpaLug as 'lugar',"
                     "format(OPAGO2.OpaEmi,'dd/MM/yyyy') as 'fecEmision',"
                     " BENEFICIAR.BenNom as 'nombreProveedor',"
                     " OPAGO2.BENCUI as 'cuit',"
                     " OPAGO2.OpaNom as 'paguese'"
                     " FROM OPAGO2 "
                     "inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
                     "where OPAGO2.OpaAnio=" + str(OpaAnio) + " AND OPAGO2.OpaNro=" + str(OpaNro) + " AND OPAGO2.jurcod='" + str(jurcod) + "' and OPAGO2.repudo='" + str(repudo) + "'")

        cursor.execute(sql_query)
        cabecera = cursor.fetchone()

        sql_query = (" SELECT  "
" ACRE001.Ac1CAn as 'ejerConstancia', "
" ACRE001.Ac1CNu as 'nroConstancia', "
" ACRE001.TReNro as 'tipoRetencion', "
" format(ACRE001.Ac1fec,'dd/MM/yyyy') as 'fecRetencion', "
" ACRE001.Ac1Est as 'estado', "
" acre001.Ac1anio as 'ejerOP', "
" ACRE001.Ac1opa as 'nroOP', "
" ACRE001.Ac1jur as 'jur', "
" ACRE001.Ac1udo as 'udo', "
" ACRE001.PopAnio as 'ejer', "
" ACRE001.Popnro as 'nroLiquidacion', "
" ACRE00.Acrmes as 'mes', "
" ACRE00.Acrano as 'anio', "
" ACRE001.Ac1Ire as 'ImporteRetenido', "
" ACRE001.Ac1Ali as 'ImporteAlicuota' "
" from ACRE001 "
" inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro  "
" where ACRE001.RfcBenCUI='"+cuit+"' AND ACRE001.Ac1Est<>'A' and ACRE001.Ac1Ire>0 and ACRE001.Ac1opa="+OpaNro+" and ACRE001.Ac1anio="+OpaAnio+" and ACRE001.Ac1jur='"+jurcod+"' and ACRE001.Ac1udo='"+repudo+"' ")
        cursor.execute(sql_query)
        detalle = cursor.fetchall()

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

        conexion = conectarSQL()
        cursor = conexion.cursor()

        sql_query = (" select  "
        " case  "
        " 	when POPAGO.Poptip='D' then 'PAGO BANCARIZADO'	 "
        " 	when POPAGO.Poptip='C' then 'PAGO CON CHEQUE'	 "	
        " end as 'tipoCpbtePago', "
        " case  "
        " 	when POPAGO.Poptip='D' then CONCAT(NOTADB.Ndbnro,'/',NOTADB.NdbAnio) "
        " 	when POPAGO.Poptip='C' then ltrim(CHEQ00.Chqnum) "
        " end as 'nroCpbtePago', "
        " case  "
        " 	when POPAGO.Poptip='D' then CONCAT(NOTADB.Cuecod,'-',NOTADB.ticcte,'-',NOTADB.Cueori) "
        " 	when POPAGO.Poptip='C' then concat(CHEQ00.Chqcta,'-',CHEQ00.Chqtip,'-',CHEQ00.Chqori) "
        " end as 'cuenta', "
        " case  "
        " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
        " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfec, 'dd/MM/yyyy') "
        " end as 'fecEmi', "
        " case  "
        " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
        " 	when POPAGO.Poptip='C' then format(CHEQ00.ChqFpg, 'dd/MM/yyyy') "
        " end as 'fecPag', "
        " case  "
        " 	when POPAGO.Poptip='D' then NOTADB.Ndbdes "
        " 	when POPAGO.Poptip='C' then CHEQ00.Chqdet "
        " end as 'detalle' "
        " from POPAGO  "
        " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
        " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
        " where POPAGO.PopAnio=" + str(OpaAnio) + " and POPAGO.Popnro='" + str(popnro) + "' and POPAGO.jurcod='" + str(jurcod) + "' and POPAGO.repudo='" + str(repudo) + "' and POPAGO.OpaNro=" + str(OpaNro) + " and PopEst<>'A' ")

        cursor.execute(sql_query)
        detalle = cursor.fetchone()
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

        conexion = conectarSQL()
        cursor = conexion.cursor()

        sql_query = ("SELECT "
          " BENEFICIAR.BENCUI as 'cuit', "
          " BENEFICIAR.BenDni as 'dni', "

          " BENEFICIAR.BenNom as 'apellidoNombre', "
          " BENEFICIAR.BenTpo as 'tipoSoc', "

          " BENEFICIAR.BenNo1 as 'nombreFantasia', "

          " format(BENEFICIAR.BenAlt, 'dd/MM/yyyy') as 'fecAlta', "
          " BENEFICIAR.BenTel as 'tel', "

          " BENEFICIAR.BenCel as 'cel', "

          " BENEFICIAR.BenMail as 'mail', "
          " case "

          " 	when BENEFICIAR.BenWap='S' then 'SI' "

          " 	when BENEFICIAR.BenWap='N' then 'NO' "
          " end as 'wappAsociado', "

          " BENEFICIAR.BenDom as 'domicilio', "

          " BENEFICIAR.BenNro as 'nroDomicilio', "
          " BENEFICIAR.PosCod as 'codPostal', "
          " POSTAL.PosLoc as 'localidad', "

          " POSTAL.PosPro as 'provincia', "
          " BENEFICIAR.BenPAl as 'pais', "

          " BENEFICIAR.BenDLe as 'domicilioLegal', "

          " BENEFICIAR.BenNLe as 'nroDomicilioLegal', "
          " BENEFICIAR.BenCPLe as 'codPostalLegal', "
          " BENEFICIAR.BenLLe as 'localidadLegal', "
          " BENEFICIAR.BenPLe as 'provinciaLegal', "
          " BENEFICIAR.BenPaLe as 'paisLegal', "

          " BENEFICIAR.BenDAl as 'domicilioAlternativo', "
          " BENEFICIAR.BenNAl as 'nroDomicilioAlternativo', "
          " BENEFICIAR.BenCPAl as 'codPostalAlternativo', "
          " BENEFICIAR.BenLAl as 'localidadAlternativo', "
          " BENEFICIAR.BenPAl as 'paisAlternativo', "

          " BENEFICIAR.BenCt3 as 'codRegistro',	 "

          " format(BENEFICIAR.BenSuF, 'dd/MM/yyyy') as 'vigenciaReg', "
          " case  "

          " 	when BENEFICIAR.BenIva='1' then 'Responsable Inscripto' "

          " 	when BENEFICIAR.BenIva='2' then 'Responsable No Inscripto' "
          " 	when BENEFICIAR.BenIva='3' then 'Exento' "

          " 	when BENEFICIAR.BenIva='4' then  'Responsable Monotributo' "
          " end as 'iva', "
          " case "

          " 	when BENEFICIAR.BenIva='4' then  BENEFICIAR.BenCat "
          " end as 'categoria', "
          " case  "

          " 	when BENEFICIAR.BenIbt='S' then 'Ingresos Brutos' "
          " 	when BENEFICIAR.BenIbt='N' then 'No Inscripto' "

          " 	when BENEFICIAR.BenIbt='M' then 'Convenio Multilateral' "
          " 	when BENEFICIAR.BenIbt='E' then 'Exento' "
          " end as 'ib', "

          " BENEFICIAR.BenIBr as 'nroIb', "

          " BENEFICIAR.BenNRes as 'resolucionIb', "

          " format(BENEFICIAR.BenVigR, 'dd/MM/yyyy' ) as 'vigenciaHasta', "
          " case  "

          " 	when BENEFICIAR.BenIgn='S' then 'Inscripto' "

          " 	when BENEFICIAR.BenIgn='I' then 'No Inscripto' "
          " 	when BENEFICIAR.BenIgn='N' then 'Exento' "
          " end as 'gan', "

          " BENEFICIAR.BenMcie as 'mesCierre', "

          " format(BENEFICIAR.BenFCS,'dd/MM/yyyy' ) as 'fecContrato', "
          " BENEFICIAR.BenRpu as 'regComercio', "
          " case "

          " 	when BENEFICIAR.BenEpl='S' then 'SI' "

          " 	when BENEFICIAR.BenEpl='N' then 'NO' "
          " end as 'empleador', "

          " BENEFICIAR.BenCGP as 'codCgp' "
          " from BENEFICIAR  "

          " inner join POSTAL on POSTAL.PosCod=BENEFICIAR.PosCod "
          " where BENEFICIAR.BENCUI= " + str(cuit))

        cursor.execute(sql_query)
        detalle = cursor.fetchone()

        sql_query = ("SELECT "
          " BFACT00.ActCod as 'codActividad', "
          " ACTIVIDAD.ActDes as 'actividad' "
          " from BFACT00 "
          " inner join ACTIVIDAD on ACTIVIDAD.ActCod= BFACT00.ActCod"
          " where BFACT00.BENCUI="+ str(cuit))

        cursor.execute(sql_query)
        actividad = cursor.fetchall()

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

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    conexion = conectarSQL()
    cursor = conexion.cursor()
    sql_query = ("SELECT  "
     " OPAGO2.OpaAnio as 'ejercicio',  "
     " OPAGO2.OpaNro as 'nroOP', "
     " OPAGO2.jurcod as 'juri', "
     " JURISDICCI.JurDes as 'jurisdiccion', "
     " OPAGO2.repudo as 'udo', "
     " REPARTICIO.RepDes as 'reparticion', "
     " format(OPAGO2.OpaEmi,'dd/MM/yyyy') as 'fecEmision', "
     " OPAGO2.OpaEst as 'estadoOPC', "
     " OPAGO2.OpaHaT as 'estadoOPT', "
     " OPAGO2.Opapgd as 'pagado', "
     " (select "
     " sum(OPAGO1.opaimp) "
     " from OPAGO1 "
     " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
     " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) as 'importeTotal', "
     "((select "
     " sum(OPAGO1.opaimp) "
     " from OPAGO1 "
     " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
     " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) - OPAGO2.Opapgd) as 'saldo' " 
     " from OPAGO2 "
     " inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
     " inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
     " inner join JURISDICCI on OPAGO2.jurcod=JURISDICCI.jurcod "
     "where opaest <> 'A' AND OPAGO2.BENCUI= " + str(cuit) + "  AND (select "
     " sum(OPAGO1.opaimp) "
     " from OPAGO1 "
     " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
     " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) > OPAGO2.Opapgd ")

    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        sql_query = sql_query + " AND OPAGO2.OpaAnio=" + request.POST.get('ejer_ajax')
    # FILTRAR POR JURISDICCION
    if request.POST.get('jur_ajax'):
        sql_query = sql_query + " AND OPAGO2.jurcod='" + str(request.POST.get('jur_ajax')) + "' "
    # FILTRAR POR UNIDAD DE JURISDICCION
    if request.POST.get('udo_ajax'):
        sql_query = sql_query + " AND OPAGO2.repudo='" + str(request.POST.get('udo_ajax')) + "' "
    # FILTRAR POR NRO DE OP
    if request.POST.get('nro_op_ajax'):
        sql_query = sql_query + " AND OPAGO2.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
    # FILTRAR POR ESTADO
    if request.POST.get('estado_ajax') != 'T':
        if request.POST.get('estado_ajax') == 'S':
         sql_query = sql_query + " AND OPAGO2.OpaEst IN ('S','H') "
        else:
            sql_query = sql_query + " AND OPAGO2.OpaEst is null "

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)


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

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    conexion = conectarSQL()
    cursor = conexion.cursor()

    sql_query = (" SELECT "
    " CASE "
    " WHEN OPAGO1.OpaCpbTip = 'FA' THEN 'Factura' "
    " WHEN OPAGO1.OpaCpbTip = 'RG' THEN 'Repos.Gasto' "
    " WHEN OPAGO1.OpaCpbTip = 'LV' THEN 'Liq.Viaticos' "
    " WHEN OPAGO1.OpaCpbTip = 'LS' THEN 'Liq.Sueldos' "
    " WHEN OPAGO1.OpaCpbTip = 'RE' THEN 'Recibo' "
    " WHEN OPAGO1.OpaCpbTip = 'TK' THEN 'Ticket' "
    " WHEN OPAGO1.OpaCpbTip = 'TR' THEN 'Transporte' "
    " WHEN OPAGO1.OpaCpbTip = 'CD' THEN 'Comp.Definitivo' "
    " WHEN OPAGO1.OpaCpbTip = 'CM' THEN 'Contrib.Municipio' "
    " WHEN OPAGO1.OpaCpbTip = 'DE' THEN 'Devolucion' "
    " WHEN OPAGO1.OpaCpbTip = 'CO' THEN 'Certif.Obra' "
    " WHEN OPAGO1.OpaCpbTip = 'PS' THEN 'PagoSeguro' "
    " WHEN OPAGO1.OpaCpbTip = 'CR' THEN 'Carg.Rendir Cta' "
    " ELSE '-' "
    " END as 'tipoCbpte', "
    " OPAGO1.OpaCpbLet as 'letraCpbte', "
    " OPAGO1.OpaSu1 as 'sucursalCpbte', "
    " OPAGO1.OpaCpbNro as 'nroCpbte', "
    " OPAGO1.OpaAnio as 'ejercicio',  "
    " OPAGO1.OpaNro as 'nroOP', "
    " OPAGO1.jurcod as 'juri', "
    " OPAGO1.repudo as 'udo', "
    " format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte', "
    " OPAGO1.OpaImp as 'importeCpbte' "
    " from OPAGO1 "
    " where OPAGO1.CpbBenCUI=" +str(cuit)+ " and OPAGO1.OpaEstL<>'A' ")

    # FILTRAR POR TIPO
    if request.POST.get('tipo_ajax') != '' :
        sql_query = sql_query + " AND OPAGO1.OpaCpbTip='" + request.POST.get('tipo_ajax') +"' "

    # FILTRAR POR LETRA
    if request.POST.get('letra_ajax') != '':
        sql_query = sql_query + " AND OPAGO1.OpaCpbLet='" + request.POST.get('letra_ajax') + "' "

    # FILTRAR POR SUCURSAL
    if request.POST.get('suc_ajax') != '':
        sql_query = sql_query + " AND OPAGO1.OpaSu1='" + request.POST.get('suc_ajax') + "' "

    # FILTRAR POR NUMERO
    if request.POST.get('nro_ajax') != '':
        sql_query = sql_query + " AND OPAGO1.OpaCpbNro like '%" + request.POST.get('nro_ajax') + "%' "

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)


def op_pagadas_excel(request):
        """ EXPORTADOR A EXCEL DE OPs PAGADAS """
        template_name = 'proveedores/op_pagadas_excel.html'

        cuit = request.user.username

        conexion = conectarSQL()
        cursor = conexion.cursor()

        if request.POST.get('tipo') == 'con':
         sql_query = (" SELECT  "
            " case  "
            " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
            " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy') "
            " end as 'fecPago', "
            "CONCAT(POPAGO.OpaAnio,POPAGO.OpaNro,POPAGO.jurcod,POPAGO.repudo) as 'aux', "                     
            " POPAGO.OpaAnio as 'ejerOP', "
            " POPAGO.Popnro as 'nroLiq', "
            " POPAGO.OpaNro as 'nroOP', "
            " POPAGO.OpaAnio as 'ejerOP', "
            " POPAGO.jurcod as 'jur', "
            " POPAGO.repudo as 'udo', "
            " REPARTICIO.RepDes as 'reparticion', "
            " case  "
            " 	when POPAGO.Poptip='D' then 'Nota Debito' "
            " 	when POPAGO.Poptip='C' then 'Cheque' "
            " 	when POPAGO.Poptip='1' then 'Ingresos Brutos' "
            " 	when POPAGO.Poptip='4' then 'Ganancias' "
            " 	when POPAGO.Poptip='X' then 'Embargo' "
            " 	when POPAGO.Poptip='7' then 'Cesion' "
            " 	when POPAGO.Poptip='R' then 'DEPOSITO DE GARANTIA' "
            " 	when POPAGO.Poptip='S' then 'SEG.SOC.(I)' "
            " 	when POPAGO.Poptip='V' then 'C.JUJ.DE LA CONST.' "
            " 	when POPAGO.Poptip='Y' then 'IMP.A LOS SELLOS' "
            " 	when POPAGO.Poptip='L' then 'FONDO LABORATORIO - D.P.V.' "
            " 	when POPAGO.Poptip='«' then 'SEGURIDAD SOCIAL 6%' "
            " 	when POPAGO.Poptip='I' then 'LEY 5118/98 VIALIDAD' "
            " 	when POPAGO.Poptip='2' then 'MULTA' "
            " 	when POPAGO.Poptip='9' then 'F.B.JUJUY S.A. 260411/03' "
            " 	when POPAGO.Poptip='G' then 'LEY 5239/00 ART.33 D.G.ARQUITECTURA' "
            " 	when POPAGO.Poptip='U' then 'SEG.SOC.(C)' "
            " 	when POPAGO.Poptip='T' then 'LEY 5118' "
            " 	when POPAGO.Poptip='E' then 'RET EARPUJ DECR. 175-G-2012' "
            " 	when POPAGO.Poptip='_' then 'CONSTANCIAS DE DEUDA'	 "
            " end as 'formaPago',  "
            " case  "
            " 	when POPAGO.Poptip='D' then CONVERT(VARCHAR,POPAGO.Ndbnro) "
            " 	when POPAGO.Poptip='C' then CONVERT(VARCHAR,POPAGO.Chqnum)	 "	
            " 	else 0 "
            " end as 'nroCpbtePago', "
            " POPAGO.Popimp as 'importe', "
            " OPAGO1.OpaCpbTip as 'tipoCbpte', "
            " OPAGO1.OpaCpbLet as 'letraCpbte', "
            " OPAGO1.OpaSu1 as 'sucursalCpbte', "
            " OPAGO1.OpaCpbNro as 'nroCpbte', "
            " format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte', "
            " OPAGO1.OpaImp as 'importeCpbte'	 "
            " from POPAGO  "
            " inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
            " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
            " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
            " inner join OPAGO1 on OPAGO1.OpaAnio=POPAGO.OpaAnio AND OPAGO1.OpaNro=POPAGO.OpaNro AND OPAGO1.jurcod=POPAGO.jurcod AND OPAGO1.repudo=POPAGO.repudo "
            " inner join BENEFICIAR on OPAGO1.CpbBenCUI=BENEFICIAR.BENCUI "
            " where OPAGO1.CpbBenCUI=" + str(cuit) + " AND POPAGO.PopEst<>'A' AND (POPAGO.Poptip='D' or POPAGO.Poptip='C') ")
        else:
         sql_query = (" SELECT  "
            " case  "
            " 	when POPAGO.Poptip='D' then format(NOTADB.Ndbfcr, 'dd/MM/yyyy')  "
            " 	when POPAGO.Poptip='C' then format(CHEQ00.Chqfpg, 'dd/MM/yyyy') "
            " end as 'fecPago', "
            " POPAGO.OpaAnio as 'ejerOP', "
            " POPAGO.Popnro as 'nroLiq', "
            " POPAGO.OpaNro as 'nroOP', "
            " POPAGO.OpaAnio as 'ejerOP', "
            " POPAGO.jurcod as 'jur', "
            " POPAGO.repudo as 'udo', "
            " REPARTICIO.RepDes as 'reparticion', "
            " case  "
            " 	when POPAGO.Poptip='D' then 'Nota Debito' "
            " 	when POPAGO.Poptip='C' then 'Cheque' "
            " 	when POPAGO.Poptip='1' then 'Ingresos Brutos' "
            " 	when POPAGO.Poptip='4' then 'Ganancias' "
            " 	when POPAGO.Poptip='X' then 'Embargo' "
            " 	when POPAGO.Poptip='7' then 'Cesion' "
            " 	when POPAGO.Poptip='R' then 'DEPOSITO DE GARANTIA' "
            " 	when POPAGO.Poptip='S' then 'SEG.SOC.(I)' "
            " 	when POPAGO.Poptip='V' then 'C.JUJ.DE LA CONST.' "
            " 	when POPAGO.Poptip='Y' then 'IMP.A LOS SELLOS' "
            " 	when POPAGO.Poptip='L' then 'FONDO LABORATORIO - D.P.V.' "
            " 	when POPAGO.Poptip='«' then 'SEGURIDAD SOCIAL 6%' "
            " 	when POPAGO.Poptip='I' then 'LEY 5118/98 VIALIDAD' "
            " 	when POPAGO.Poptip='2' then 'MULTA' "
            " 	when POPAGO.Poptip='9' then 'F.B.JUJUY S.A. 260411/03' "
            " 	when POPAGO.Poptip='G' then 'LEY 5239/00 ART.33 D.G.ARQUITECTURA' "
            " 	when POPAGO.Poptip='U' then 'SEG.SOC.(C)' "
            " 	when POPAGO.Poptip='T' then 'LEY 5118' "
            " 	when POPAGO.Poptip='E' then 'RET EARPUJ DECR. 175-G-2012' "
            " 	when POPAGO.Poptip='_' then 'CONSTANCIAS DE DEUDA' "	
            " end as 'formaPago',  "
            " case  "
            " 	when POPAGO.Poptip='D' then CONVERT(VARCHAR,POPAGO.Ndbnro) "
            " 	when POPAGO.Poptip='C' then CONVERT(VARCHAR,POPAGO.Chqnum)		 "
            " 	else 0 "
            " end as 'nroCpbtePago', "
            " POPAGO.Popimp as 'importe' "
            " from POPAGO  "
            " inner join OPAGO2 on POPAGO.OpaAnio=OPAGO2.OpaAnio AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod AND POPAGO.repudo=OPAGO2.repudo "
            " inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
            " left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
            " left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
            " WHERE OPAGO2.BENCUI=" + str(cuit) + " AND POPAGO.PopEst<>'A' AND (POPAGO.Poptip='D' or POPAGO.Poptip='C') ")


        # FILTRAR POR EJERCICIO
        if request.POST.get('ejer_ajax'):
            sql_query = sql_query + " AND POPAGO.OpaAnio=" + request.POST.get('ejer_ajax')
        # FILTRAR POR JURISDICCION
        if request.POST.get('jur_ajax'):
            sql_query = sql_query + " AND POPAGO.jurcod=" + request.POST.get('jur_ajax')
        # FILTRAR POR UNIDAD DE JURISDICCION
        if request.POST.get('udo_ajax'):
            sql_query = sql_query + " AND POPAGO.repudo=" + request.POST.get('udo_ajax')
        # FILTRAR POR NRO DE OP
        if request.POST.get('nro_op_ajax'):
            sql_query = sql_query + " AND POPAGO.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
        # FILTRAR POR FECHA DESDE
        if request.POST.get('desde_ajax'):
            sql_query = sql_query + " AND POPAGO.Popfpg>='" + request.POST.get('desde_ajax') + "'"
        # FILTRAR POR FECHA HASTA
        if request.POST.get('hasta_ajax'):
            sql_query = sql_query + " AND POPAGO.Popfpg<='" + request.POST.get('hasta_ajax') + "'"

        cursor.execute(sql_query)
        comprobante = cursor.fetchall()

        context = {
            "comprobante": comprobante,
            "tipo" : request.POST.get('tipo')
        }

        return generate_excel(request, template_name, context)


def op_impagas_excel(request):
    """ EXPORTADOR A EXCLE DE OPs IMPAGAS """
    template_name = 'proveedores/op_impagas_excel.html'

    cuit = request.user.username

    conexion = conectarSQL()
    cursor = conexion.cursor()

    if request.POST.get('tipo') == 'con':
      sql_query = (" SELECT  "
      " OPAGO2.OpaAnio as 'ejerOP', "
      " OPAGO2.OpaNro as 'nroOP', "
      " OPAGO2.jurcod as 'jur', "
      " OPAGO2.repudo as 'udo', "
      " format( OPAGO2.OpaEmi ,'dd/MM/yyyy') as 'fecEmi', "
      " REPARTICIO.RepDes as 'reparticion', "
      " OPAGO1.OpaCpbTip as 'tipoCbpte', "
      " OPAGO1.OpaCpbLet as 'letraCpbte', "
      " OPAGO1.OpaSu1 as 'sucursalCpbte', "
      " OPAGO1.OpaCpbNro as 'nroCpbte', "
      " (select  "
      " sum(opago1.opaimp)  "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND  "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo "
      " ) as 'ImporteTotalOP', "
      " opago2.opapgd as 'pagado', "
      " (select  "
      " sum(opago1.opaimp)  "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND  "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) - opago2.opapgd as 'SaldoOP', "
      " format( OPAGO1.OpaCpcFec ,'dd/MM/yyyy') as 'fecCpbte', "
      " OPAGO1.OpaImp as 'importeCpbte', "
      " OPAGO2.OpaEst as 'habilitaContad', "
      " OPAGO2.OpaHaT as 'habilitaTeso' "
      " from OPAGO2  "
      " inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
      " inner join OPAGO1 on OPAGO1.OpaAnio=OPAGO2.OpaAnio AND OPAGO1.OpaNro=OPAGO2.OpaNro AND OPAGO1.jurcod=OPAGO2.jurcod AND OPAGO1.repudo=OPAGO2.repudo "
      " inner join BENEFICIAR on OPAGO1.CpbBenCUI=BENEFICIAR.BENCUI "
      " where OPAGO1.CpbBenCUI="+  str(cuit) +"  AND (select "
      " sum(OPAGO1.opaimp) "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) > OPAGO2.Opapgd  AND OPAGO2.OpaEst<>'A' ")
    else:
        sql_query = ("SELECT  "
      " OPAGO2.OpaAnio as 'ejerOP', "
      " OPAGO2.OpaNro as 'nroOP', "
      " OPAGO2.jurcod as 'jur', "
      " JURISDICCI.JurDes as 'jurisdiccion', "
      " OPAGO2.repudo as 'udo', "
      " REPARTICIO.RepDes as 'reparticion', "
      " format( OPAGO2.OpaEmi ,'dd/MM/yyyy') as 'fecEmi', "
      " OPAGO2.OpaEst as 'estadoOPC', "
      " OPAGO2.OpaHaT as 'estadoOPT', "
      " OPAGO2.Opapgd as 'pagado', "
      " (select "
      " sum(OPAGO1.opaimp) "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) as 'ImporteTotalOP', "
      "((select "
      " sum(OPAGO1.opaimp) "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) - OPAGO2.Opapgd) as 'SaldoOP', "
      " OPAGO2.OpaEst as 'habilitaContad', "
      " OPAGO2.OpaHaT as 'habilitaTeso' "               
      " from OPAGO2 "
      " inner join REPARTICIO on OPAGO2.jurcod=REPARTICIO.jurcod and OPAGO2.repudo=REPARTICIO.repudo "
      " inner join BENEFICIAR on OPAGO2.BENCUI=BENEFICIAR.BENCUI "
      " inner join JURISDICCI on OPAGO2.jurcod=JURISDICCI.jurcod "
      "where opaest <> 'A' AND OPAGO2.BENCUI= " + str(cuit) + "  AND (select "
      " sum(OPAGO1.opaimp) "
      " from OPAGO1 "
      " where OPAGO2.OpaAnio=OPAGO1.OpaAnio AND OPAGO2.OpaNro=OPAGO1.OpaNro AND "
      " OPAGO2.jurcod=OPAGO1.jurcod and OPAGO2.repudo=OPAGO1.repudo) > OPAGO2.Opapgd ")

    # FILTRAR POR EJERCICIO
    if request.POST.get('ejer_ajax'):
        sql_query = sql_query + " AND OPAGO2.OpaAnio=" + request.POST.get('ejer_ajax')
    # FILTRAR POR JURISDICCION
    if request.POST.get('jur_ajax'):
        sql_query = sql_query + " AND POPAGO2.jurcod=" + request.POST.get('jur_ajax')
    # FILTRAR POR UNIDAD DE JURISDICCION
    if request.POST.get('udo_ajax'):
        sql_query = sql_query + " AND POPAGO2.repudo=" + request.POST.get('udo_ajax')
    # FILTRAR POR NRO DE OP
    if request.POST.get('nro_op_ajax'):
        sql_query = sql_query + " AND POPAGO2.OpaNro like '%" + request.POST.get('nro_op_ajax') + "%'"
    # FILTRAR POR ESTADO
    if request.POST.get('estado_ajax') != 'T':
        if request.POST.get('estado_ajax') == 'S':
         sql_query = sql_query + " AND OPAGO2.OpaEst IN ('S','H') "
        else:
            sql_query = sql_query + " AND OPAGO2.OpaEst is null "

    cursor.execute(sql_query)
    comprobante = cursor.fetchall()

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

    # ARMAR PRIMER OBJETO CON NRO DE CUIL
    conexion = conectarSQL()
    cursor = conexion.cursor()

    sql_query = ("SELECT  "
"  ACRE001.Ac1CAn as 'ejerConstancia', "
"  ACRE001.Ac1CNu as 'nroConstancia', "
"  ACRE001.TReNro as 'tipoRetencion', "
"  format(ACRE001.Ac1fec,'dd/MM/yyyy') as 'fecRetencion', "
"  ACRE001.Ac1Est as 'estado', "
"  ACRE001.Ac1opa as 'nroOP', "
"  ACRE001.Ac1jur as 'jur', "
"  ACRE001.Ac1udo as 'udo', "
"  ACRE001.PopAnio as 'ejer', "
"  ACRE001.Popnro as 'nroLiquidacion', "
"  ACRE00.Acrmes as 'mes', "
"  ACRE00.Acrano as 'anio', "
"  ACRE001.Ac1Ire as 'ImporteRetenido' "
"  from ACRE001 "
"  inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro "
"  where ACRE001.RfcBenCUI="+cuit+" AND ACRE001.Ac1Est<>'A' and ACRE001.Ac1Ire > 0 ")

    # FILTRAR POR TIPO
    if request.POST.get('tipo_ajax'):
        sql_query = sql_query + " AND ACRE001.TReNro=" + request.POST.get('tipo_ajax')

    # FILTRAR POR FECHA DESDE
    if request.POST.get('desde_ajax'):
        sql_query = sql_query + " AND ACRE001.Ac1fec>='" + request.POST.get('desde_ajax') + "'"
    # FILTRAR POR FECHA HASTA
    if request.POST.get('hasta_ajax'):
        sql_query = sql_query + " AND ACRE001.Ac1fec<='" + request.POST.get('hasta_ajax') + "'"

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)



def op_retenciones_pdf(request):
    """ IMPRESOR DE RETENCIONES """
    template_name = 'proveedores/op_retenciones_pdf.html'
    cuit = request.user.username
    tipo = request.POST.get('tipo')
    anio = request.POST.get('anio')
    cons = request.POST.get('cons')
    trenro = request.POST.get('trenro')

    conexion = conectarSQL()
    cursor = conexion.cursor()

    if tipo == '4':
      sql_query = (" SELECT "
      " ACRE001.Ac1CNu as 'nroConstancia', "
      " ACRE001.Ac1CAn as 'ejerConstancia', "
      " format(ACRE001.Ac1fec,'dd/MM/yyyy') as 'fecha', "
      " BENEFICIAR.BenNom as 'contribuyente', "
      " ACRE001.RfcBenCUI as 'cuit', "
      " CONCAT(LTRIM(BENEFICIAR.BenDom),' ',LTRIM(BENEFICIAR.BenNro),' ',LTRIM(POSTAL.PosLoc),' ',LTRIM(POSTAL.PosPro)) as 'domicilio', "
      " REGACT.ImpDes as 'impuesto', "
      " REGI00.RegDes as 'regimen', "
      " (select sum(ACRE001.Ac1Ipg) from ACRE001  "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=4) as 'importeOper', "
      " ACRE001.CpbTip as 'tipoCbpte', "
      " ACRE001.CpbLet as 'letraCpbte', "
      " ACRE001.Ac1Su1 as 'sucursalCpbte', "
      " ACRE001.CpbNro as 'nroCpbte', "
      " acre001.ac1ipg as 'importeCpbte', "
      " acre001.ac1opa as 'NroOP', "
      " acre001.ac1jur as 'jur', "
      " acre001.ac1udo as 'udo', "
      " (select sum(ACRE001.Ac1Ire) from ACRE001  "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=4) as 'importeReten' "
      " from ACRE001 "
      " inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro " 
      " inner join BENEFICIAR on ACRE001.RfcBenCUI=BENEFICIAR.BENCUI "
      " inner join POSTAL on BENEFICIAR.PosCod=POSTAL.PosCod "
      " inner join BFACT00 ON BFACT00.BENCUI=ACRE00.RfcBenCUI and BFACT00.ActCod=ACRE001.Ac1Act "
      " inner join REGACT on BFACT00.ActCod=REGACT.ActCod "
      " inner join REGI00 on REGI00.REGCod=REGACT.REGCOD "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=4 ")

    elif tipo == '1':
      sql_query = (" SELECT "
      " ACRE001.Ac1CAn as 'ejerConstancia', "
      " ACRE001.Ac1CNu as 'nroConstancia', "
      " BENEFICIAR.BenNom as 'contribuyente', "
      " ACRE001.RfcBenCUI as 'cuit', "
      " format(ACRE001.Ac1fec,'dd/MM/yyyy') as 'fecRetencion', "
      " ACRE001.Popnro as 'nroLiquidacion', "
      " ACRE001.CpbTip as 'tipoCbpte', "
      " ACRE001.CpbLet as 'letraCpbte', "
      " ACRE001.Ac1Su1 as 'sucursalCpbte', "
      " ACRE001.CpbNro as 'nroCpbte', "
      " acre001.ac1ipg as 'importeCpbte', "
      " (select sum(ACRE001.Ac1Ipg) from ACRE001  "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=1) as 'importeOper', "
      " (select sum(ACRE001.Ac1Ire) from ACRE001  "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=1) as 'importeReten', "
      " ACRE001.Ac1Ali as 'alicuota' "
      " from ACRE001 "
      " inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro  "
      " inner join BENEFICIAR on ACRE001.RfcBenCUI=BENEFICIAR.BENCUI "
      " where  ACRE001.RfcBenCUI=" +str(cuit)+ " and ACRE001.Ac1CAn=" +str(anio)+ " and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro=1 ")
    else:
      sql_query = (" SELECT  "
      " ACRE001.Ac1CNu as 'nroConstancia', "
      " ACRE001.Ac1CAn as 'ejerConstancia', "
      " BENEFICIAR.BenNom as 'contribuyente', "
      " CONCAT(LTRIM(BENEFICIAR.BenDom),' ',LTRIM(BENEFICIAR.BenNro),' ',LTRIM(POSTAL.PosLoc),' ',LTRIM(POSTAL.PosPro)) as 'domicilio', "
      " ACRE001.RfcBenCUI as 'cuit', "
      " ACRE001.Ac1Ali as 'alicuota', "
      " (select sum(ACRE001.Ac1Ipg) from ACRE001  "
      " where  ACRE001.RfcBenCUI="+str(cuit)+" and ACRE001.Ac1CAn="+str(anio)+" and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro<>1 AND ACRE001.TReNro<>4) as 'importeOper', "
      " (select sum(ACRE001.Ac1Ire) from ACRE001  "
      " where  ACRE001.RfcBenCUI="+str(cuit)+" and ACRE001.Ac1CAn="+str(anio)+" and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro<>1 AND ACRE001.TReNro<>4) as 'importeReten', "
      " format(ACRE001.Ac1fec,'dd/MM/yyyy') as 'fecRetencion', "
      " ACRE001.Popnro as 'nroLiquidacion', "
      " ACRE001.Popanio as 'ejerLiquidacion' "
      " from ACRE001 "
      " inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro " 
      " inner join BENEFICIAR on ACRE001.RfcBenCUI=BENEFICIAR.BENCUI "
      " inner join POSTAL on BENEFICIAR.PosCod=POSTAL.PosCod "
      " where  ACRE001.RfcBenCUI="+str(cuit)+" and ACRE001.Ac1CAn="+str(anio)+" and ACRE001.Ac1CNu="+ str(cons) +" AND ACRE001.TReNro<>1 AND ACRE001.TReNro<>4 ")


    cursor.execute(sql_query)
    comprobante = cursor.fetchone()

    context = {
        'tipo': tipo,
        'comprobante': comprobante
    }

    return generate_pdf(request, template_name, context)

def op_retenciones_excel(request):
        """ EXPORTADOR A EXCEL DE RETENCIONES """
        template_name = 'proveedores/op_retenciones_excel.html'

        cuit = request.user.username

        conexion = conectarSQL()
        cursor = conexion.cursor()

        sql_query = (" SELECT "
                     " ACRE001.Ac1CAn as 'ejerConstancia', "
                     " ACRE001.Ac1CNu as 'nroConstancia', "
                     " ACRE001.TReNro as 'tipoRetencion', "
                     " format( ACRE001.Ac1fec ,'dd/MM/yyyy') as 'fecRetencion', "
                     " ACRE001.Ac1Est as 'estado', "
                     " ACRE001.Ac1opa as 'nroOP', "
                     " ACRE001.Ac1jur as 'jur', "
                     " ACRE001.Ac1udo as 'udo', "
                     " ACRE001.PopAnio as 'ejer', "
                     " ACRE001.Popnro as 'nroLiquidacion', "
                     " ACRE00.Acrmes as 'mes', "
                     " ACRE00.Acrano as 'anio', "
                     "ACRE001.TReNro"
                     " from ACRE001 "
                     " inner join ACRE00 on ACRE001.RfcBenCUI=ACRE00.RfcBenCUI and ACRE001.Acrano=ACRE00.Acrano and ACRE001.Acrmes=ACRE00.Acrmes and ACRE001.TReNro=ACRE00.TReNro "
                     " where ACRE001.RfcBenCUI="+cuit+" AND ACRE001.Ac1Est<>'A' ")

        # FILTRAR POR TIPO
        if request.POST.get('tipo_ajax'):
            sql_query = sql_query + " AND ACRE001.TReNro=" + request.POST.get('tipo_ajax')

        # FILTRAR POR FECHA DESDE
        if request.POST.get('desde_ajax'):
            sql_query = sql_query + " AND ACRE001.Ac1fec>='" + request.POST.get('desde_ajax') + "'"
        # FILTRAR POR FECHA HASTA
        if request.POST.get('hasta_ajax'):
            sql_query = sql_query + " AND ACRE001.Ac1fec<='" + request.POST.get('hasta_ajax') + "'"


        cursor.execute(sql_query)
        datos = cursor.fetchall()

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

