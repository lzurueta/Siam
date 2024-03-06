import math
import tempfile

import pymssql
import pyodbc
from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML
#import logging
#logger = logging.getLogger('weasyprint')
#logger.addHandler(logging.FileHandler('/var/log/weasyprint.log'))

def generate_pdf(request, template, texto, attachments=None):
    # Rendered
    html_string = render_to_string(template, texto)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
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
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html.write_pdf(nombre_archivo, presentational_hints=True, attachments=attachments)
    return True



def conectarSQL():
    direccion_servidor = '123.123.123.45'
    instancia = "srv-lab"
    nombre_bd = 'siaf'
    nombre_usuario = 'siafsql'
    password = '159753'

    #conexion = pymssql.connect(direccion_servidor, nombre_usuario, password, nombre_bd)

    #conexion = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=' +
    #                          direccion_servidor + ';INSTANCE=' + instancia + ';DATABASE=' + nombre_bd + ';UID='
    #                          + nombre_usuario + ';PWD=' + password + ';Encrypt=No;TrustServerCertificate=Yes;Trusted_Connection=Yes')

    conexion = pyodbc.connect('DSN=siafprueba;UID=siafsql;PWD=159753;')

    return conexion

