from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from sistema.models import Profile
class administracion_usuarios(View):
    template_name = 'administrador/administrador_usuarios.html'

    def get_context_data(self, **kwargs):

        context = {
            'titulo': "Administrador de Usuarios",
        }
        return context
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())



class administracion_usuarios_ajax(View):
    """COMPLETAR DATOS DE TABLA DE USUARIOS CON FILTROS"""
    def post(self, request):
        perfil = Profile.objects.values('user', 'user__username', 'user__is_active', 'nombre', 'nombreResponsable', 'apellidoResponsable', 'dni', 'direccion', 'telefono', 'caracter', 'email')

        cuit = request.POST.get('cuit_ajax')
        rs = request.POST.get('rs_ajax')
        mail = request.POST.get('mail_ajax')
        celular = request.POST.get('celular_ajax')
        nombre = request.POST.get('nombre_ajax')
        apellido = request.POST.get('apellido_ajax')
        dni = request.POST.get('dni_ajax')
        direccion = request.POST.get('domicilio_ajax')

        if cuit:
            perfil = perfil.filter(user__username__icontains=cuit)
        if rs:
            perfil = perfil.filter(nombre__icontains=rs)
        if mail:
            perfil = perfil.filter(email__icontains=mail)
        if celular:
            perfil = perfil.filter(telefono__icontains=celular)
        if nombre:
            perfil = perfil.filter(nombreResponsable__icontains=nombre)
        if apellido:
            perfil = perfil.filter(apellidoResponsable__icontains=apellido)
        if dni:
            perfil = perfil.filter(dni__icontains=dni)
        if direccion:
            perfil = perfil.filter(direccion__icontains=direccion)

        data = list(perfil)
        return JsonResponse(data, safe=False)

def administracion_usuarios_estado(request):
    """CAMBIAR DE ESTADO DE USUARIO"""
    user = request.POST.get('user')
    aux = request.POST.get('estado')
    estado = aux.capitalize()

    usuario = User.objects.get(id=user)
    usuario.is_active = estado
    usuario.save()

    profile = Profile.objects.get(user=usuario)

    if estado == 'True':
        profile.activate_at = timezone.now()
    else:
        profile.disabled_at = timezone.now()

    profile.save()

    return HttpResponse()