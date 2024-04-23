from django.shortcuts import render
from django.views import View
from sistema.functions import traerIndex
# Create your views here.

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

