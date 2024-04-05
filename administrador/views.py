from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from sistema.models import Profile
import random
import string
from django.core.mail import send_mail

from sistema.functions import generate_pdf


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


def administracion_usuarios_actualizar_clave(request):
    """GENERADOR DE NUEVA CLAVE DE USUARIO"""

    user = request.POST.get('user')
    letras_mayusculas = string.ascii_uppercase
    letras_minusculas = string.ascii_lowercase
    digitos = string.digits
    caracteres_especiales = './?@#$%&*()-_+'

    cadena = (random.choice(letras_mayusculas) +
              random.choice(letras_minusculas) +
              random.choice(digitos))

    cadena += ''.join(random.choice(letras_mayusculas + letras_minusculas + digitos) for _ in range(8))


    posicion_caracter_especial = random.randint(0, len(cadena) - 1)
    cadena = cadena[:posicion_caracter_especial] + random.choice(caracteres_especiales) + cadena[ posicion_caracter_especial + 0:]

    cadena_lista = list(cadena)
    random.shuffle(cadena_lista)
    cadena = ''.join(cadena_lista)

    usuario = User.objects.get(id=user)
    usuario.set_password(cadena)
    usuario.save()

    profile = Profile.objects.get(user=user)

    srcImg = 'data:image/png;base64,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'



    html = ('<p style="font-size:12px;">Estimada/o Proveedor</p>'
            '<p style="font-size:12px;">Se actualizó la contraseña de su usuario '+ usuario.username +'</p>'
            '<p style="font-size:12px;">Nueva Contraseña: <b>'+cadena+'</b></p>'
            '<p style="font-size:12px;margin-top:20px"><img src="'+srcImg+'" width="110px" alt=""><br><br>Secretaria de Informática<br>Ministerio de Hacienda y Finanzas</p>'
            '<p><hr style="width:100%"></p>'
            '<p style="font-size:8px;">*Este es un mensaje automático. Por favor, no responda a este correo electrónico.</p>')

    send_mail(
        'Actualización de Contraseña - Sistema de Proveedores.',
        '',
        'tesoreria@jujuy.gob.ar',
        [profile.email],
        html_message=html,
    )

    return JsonResponse({'clave': cadena})


def imprimir_dj(request):

    template_name = 'registration/declaracion_jurada_pdf.html'
    profile = Profile.objects.get(user=request.POST.get('user'))

    context = {
        'profile': profile
    }

    return generate_pdf(request, template_name, context)
