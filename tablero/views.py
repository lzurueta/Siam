from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from sistema.functions import traerIndex
from sistema.functions import conectarSQLTablero

class principal(View):
    template_name = 'tablero/principal.html'

    def get_context_data(self, **kwargs):



        context = {
            'titulo': "Tablero de Control",
            'index' : traerIndex(self.request)
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

def principal_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA CON FILTROS DE BUSQUEDA """

    anio = request.POST.get('anio_ajax')
    mes = request.POST.get('mes_ajax')

    conexion = conectarSQLTablero()
    cursor = conexion.cursor()
    sql_query = ("SELECT a.repjur, a.JurNom, a.cantidad, FORMAT(a.remunerativo, 'C', 'es-AR') as remunerativoFormat, FORMAT(a.noRemunerativo, 'C', 'es-AR') as noRemunerativoFormat, FORMAT(a.total, 'C', 'es-AR') as totalFormat, "
                 " (a.total * 100) / total_general.total_todos AS porcentaje "
                 " FROM (SELECT "
                 "     sector.repjur, "
                 "     sector.JurNom, "
                 "     (SELECT COUNT(c.cont) FROM (SELECT COUNT(DETLIQ.pecuil) as cont "
                 "      FROM DETLIQ "
                 "      WHERE "
                 "          DETLIQ.DetAno = '"+anio+"' "
                 "          AND DETLIQ.DetMes = "+mes+" "
                 " 		 AND DETLIQ.repjur = sector.repjur "
                 "          AND DETLIQ.JurNom = sector.JurNom "
                 " 		 GROUP BY pecuil) as c) AS cantidad, "
                 " 		SUM(CASE WHEN sector.deprt = 1 THEN sector.deval ELSE 0 END) AS remunerativo, "
                 "         SUM(CASE WHEN sector.deprt = 2 THEN sector.deval ELSE 0 END) AS noRemunerativo, "
                 " 		SUM(CASE WHEN deprt IN (1,2) THEN deval ELSE 0 END) AS total "
                 " FROM "
                 "     DETLIQ AS sector "
                 " WHERE "
                 "     sector.DetAno = '"+anio+"' "
                 "     AND sector.DetMes = "+mes+" "
                 " GROUP BY "
                 "     sector.repjur, "
                 "     sector.JurNom) as a "
                 " CROSS JOIN ( "
                 "     SELECT SUM(CASE WHEN deprt IN (1,2) THEN deval ELSE 0 END) AS total_todos "
                 "     FROM DETLIQ "
                 "     WHERE DetAno = '"+anio+"' AND DetMes = "+mes+" ) AS total_general "
                 " ORDER BY a.total DESC; ")

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT
    data = list(results)
    return JsonResponse(data, safe=False)

def table_personas_ajax(request):
    """ FUNCION PARA TRAER DATOS DE LA TABLA DE PERSONAS """

    anio = request.POST.get('anio')
    mes = request.POST.get('mes')
    jur = request.POST.get('jur')
    jurNombre = request.POST.get('jurNombre')

    conexion = conectarSQLTablero()
    cursor = conexion.cursor()
    sql_query = ("SELECT  "
    "pecuil,  "
    "UPPER(Peayn) AS nombre, "
    "EsDes, "
    "repdes, "
    "CatDes, "
    "FORMAT(SUM(CASE WHEN deprt = 1 THEN deval ELSE 0 END), 'C', 'es-AR') AS remunerativo, "
    "FORMAT(SUM(CASE WHEN deprt = 2 THEN deval ELSE 0 END), 'C', 'es-AR') AS noRemunerativo, "
    "FORMAT(SUM(CASE WHEN deprt IN (1,2) THEN deval ELSE 0 END), 'C', 'es-AR') AS total "
    "FROM DETLIQ  "
    "WHERE  "
    "DETLIQ.DetAno = '"+anio+"'  "
    "AND DETLIQ.DetMes = "+mes+"  "
    "AND DETLIQ.repjur = '"+jur+"' "
    "AND DETLIQ.JurNom = '"+jurNombre+"' "
    "GROUP BY pecuil, Peayn, EsDes, repdes, CatDes "
    "ORDER BY CatDes ")

    cursor.execute(sql_query)
    ## CONVERTIR EL CURSOR EN DICT
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    ## CONVERTIR EL CURSOR EN DICT

    data = list(results)
    return JsonResponse(data, safe=False)

