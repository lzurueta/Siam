from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

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
<<<<<<< HEAD
        cuit = 30718402235
=======
        cuit = 30718402234
>>>>>>> b54cab0a7304cc54675332aacb8a70b5bf250b90
        pagadas = CPOPAGO.objects.filter(cbencui=cuit)
        if self.request.POST.get('nro_op'):
            pagadas = pagadas.filter(copanro=self.request.POST.get('nro_op'))
        if self.request.POST.get('desde'):
            pagadas = pagadas.filter(cpopfpg__gte=self.request.POST.get('desde'))
<<<<<<< HEAD
=======
        cuit = 30718402235
        anio = timezone.now().year

        # ARMAR PRIMER OBJETO CON NRO DE CUIL
        conexion = conectarSQL()
        cursor = conexion.cursor(as_dict=True)
        sql_query = ("SELECT * FROM POPAGO INNER JOIN OPAGO2 ON POPAGO.OpaAnio=OPAGO2.OpaAnio "
                     "AND POPAGO.OpaNro=OPAGO2.OpaNro AND POPAGO.jurcod=OPAGO2.jurcod "
                     "AND POPAGO.repudo=OPAGO2.repudo WHERE POPAGO.OpaAnio=" + str(anio) + " AND OPAGO2.BENCUI=") + str(cuit)
        cursor.execute(sql_query)

>>>>>>> b54cab0a7304cc54675332aacb8a70b5bf250b90
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

class op_pagadas_imprimir(View):
    template_name = 'proveedores/op_pagadas_pdf.html'

    def get(self, request, *args, **kwargs):
        op_pagada = CPOPAGO.objects.get(id=kwargs['id'])
        context = {
            'op_pagada': op_pagada,
        }
        return generate_pdf(request, self.template_name, context)

