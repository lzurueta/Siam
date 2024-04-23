import math
import tempfile

import pymssql
import pyodbc
import openpyxl
import io

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from openpyxl import Workbook
from django.template.loader import render_to_string
from bs4 import BeautifulSoup


#import logging
#logger = logging.getLogger('weasyprint')
#logger.addHandler(logging.FileHandler('/var/log/weasyprint.log'))


def generate_excel(request, template, texto):

    html_string = render_to_string(template, texto)

    print(texto)

    workbook = Workbook()
    sheet = workbook.active

    soup = BeautifulSoup(html_string, 'html.parser')

    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        for row_index, row in enumerate(rows, start=1):
            cells = row.find_all(['th', 'td'])
            for col_index, cell in enumerate(cells, start=1):
                sheet.cell(row=row_index, column=col_index, value=cell.get_text(strip=True))

    excel_data = io.BytesIO()
    workbook.save(excel_data)

    excel_data.seek(0)

    response = HttpResponse(excel_data.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=excel.xlsx'

    return response


def generate_pdf(request, template, texto, attachments=None):
    # Rendered
    html_string = render_to_string(template, texto)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html = HTML(string=html_string, base_url='.')
    result = html.write_pdf(presentational_hints=True, attachments=attachments)

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=pdf.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response


def generate_pdf_save(request, template, texto, nombre_archivo, attachments=None):
    # Rendered
    html_string = render_to_string(template, texto)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html = HTML(string=html_string, base_url='.')
    html.write_pdf(nombre_archivo, presentational_hints=True, attachments=attachments)
    return True



def conectarSQL():
    direccion_servidor = '123.123.123.45'
    instancia = "srv-lab"
    nombre_bd = 'siaf'
    nombre_usuario = 'siafsql'
    password = '159753'

    #### MAC Y LINUX
    conexion = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + direccion_servidor + ', 1433;DATABASE=' + nombre_bd + ';UID=' + nombre_usuario + ';PWD=' + password + ';Encrypt=no;')

    #### WINDOWS
    # conexion = pyodbc.connect('DSN=siafprueba;UID=siafsql;PWD=159753;')

    return conexion

def traerIndex(request):
    grupos_usuario = request.user.groups.all()

    if grupos_usuario.filter(name='Tablero').exists():
        index = '/tablero/'

    elif grupos_usuario.filter(name='Prensa').exists():
        index = '/prensa/'

    else:
        index = '/sistema/'

    return index