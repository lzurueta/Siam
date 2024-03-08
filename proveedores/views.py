from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View

from num2words import num2words


from proveedores.models import CPOPAGO
from sistema.functions import generate_pdf, conectarSQL

import datetime
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
        anio = datetime.datetime.now().year

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
        "OPAGO2.BENCUI as 'cuit',"
        "POPAGO.Popnro as 'popnro'"
        "from POPAGO "
        "inner join OPAGO2 on POPAGO.OpaAnio=OPAGO2.OpaAnio AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod AND POPAGO.repudo=OPAGO2.repudo "
        "left join CHEQ00 on CHEQ00.Chqnum=POPAGO.Chqnum and CHEQ00.Chqcta=POPAGO.Chqcta and CHEQ00.Chqtip=POPAGO.Chqtip "
        "left join NOTADB on NOTADB.NdbAnio=POPAGO.NdbAnio and NOTADB.Ndbnro=POPAGO.Ndbnro "
        "inner join REPARTICIO on POPAGO.jurcod=REPARTICIO.jurcod and POPAGO.repudo=REPARTICIO.repudo "
        "where POPAGO.PopEst<>'A' AND POPAGO.OpaAnio= " + str(anio) + " AND OPAGO2.BENCUI= " + str(cuit) )
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


class op_pagadas_imprimir(View):
    """ IMPRESOR DE OP """
    template_name = 'proveedores/op_pagadas_pdf.html'

    def get(self, request, *args, **kwargs):

        OpaAnio = kwargs['OpaAnio']
        OpaNro = kwargs['OpaNro']
        jurcod = kwargs['jurcod']
        repudo = kwargs['repudo']

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
                     " OPAGO2.OpaNom as 'paguese'"
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
                     "SUM(OPAGO1.OpaImp) as 'importeCpbte'"
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

        saldo = total[0] - totalPagosAsoc[0]

        context = {
            'cabecera': cabecera,
            'detalle': detalle,
            'importeTexto': decimal_a_texto(total[0]),
            'importe': total[0],
            'pagosAsociados': pagosAsociados,
            'saldo': saldo

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
    "where OPAGO2.BENCUI=30718402235 and POPAGO.PopEst<>'A' ")


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
    # FILTRAR POR TIPOS DE CHEQUES
    if request.POST.get('cheque_ajax'):
        #FALTA HACER
        sql_query = sql_query

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)


def op_pagadas_detalle(request):
    """ VISTA DE DETALLE DE ORDEN DE COMPRA """ 
    template_name = 'proveedores/op_pagadas_detalle.html'

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