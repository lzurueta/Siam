import importlib

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from sistema.forms import NewUserForm


# Create your views here.
class SistemaHome(View):

    def get_context_data(self, **kwargs):
        context = {
            'titulo': "Profile",
        }
        return context

    def get(self, request, *args, **kwargs):
        if request.user.groups.first():
            return redirect(request.user.groups.first().home)
        template_name = 'sistema/profile.html'
        return render(request, template_name, self.get_context_data())


def registerUser(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registración Exitosa.")
            return redirect("index")
        messages.error(request, form.errors)
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


class ProfileView(View):

    def get_context_data(self, **kwargs):
        context = {
            'titulo': "Profile",
        }
        return context

    def get(self, request, *args, **kwargs):
        template_name = 'sistema/profile.html'
        return render(request, template_name, self.get_context_data())


class logout_view(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        # Redirect to a success page.
        return redirect('index')


def importar_formulario(app_name, form_name):
    try:
        # Construye el nombre del módulo que contiene el formulario
        nombre_del_modulo = f"apps.{app_name}.forms"

        # Importa el módulo utilizando importlib
        modulo = importlib.import_module(nombre_del_modulo)

        # Obtén la clase del formulario desde el módulo
        formulario_cls = getattr(modulo, form_name)

        return formulario_cls
    except (ImportError, AttributeError):
        return None


def generarABM(request, context):
    template_name = 'sistema/abm.html'
    app_name = context.get('app_name')
    model_name = context.get('model_name')
    form_name = context.get('form_name')
    list_display = context.get('list_display')
    botones = context.get('botones')
    filtro = context.get('filtro')
    padre = context.get('padre')
    field_name = None
    field_value = None
    personaopera = None
    if context.get('personaopera'):
        personaopera = context.get('personaopera')
    if padre:
        for clave, valor in padre.items():
            field_name = clave
            field_value = valor

    model = apps.get_model(app_name, model_name)
    form = importar_formulario(app_name, form_name)

    list_display2 = []
    for list in list_display:
        list_display2.append(model._meta.get_field(list).verbose_name)
    object_values = []
    objects = model.objects.all()
    if filtro:
        objects = model.objects.filter(**filtro)
    for object in objects:
        object_values.append([])
        for field in list_display:
            object_values[-1].append(getattr(object, field))
        object_values[-1].append(getattr(object, 'id'))

    context = {
        'titulo': model._meta.verbose_name_plural,
        'objetos': object_values,
        'form': form,
        'list_display': list_display2,
        'botones': botones,
        'app_name': app_name,
        'model_name': model_name,
        'form_name': form_name,
        'padre': padre,
        'field_name': field_name,
        'field_value': field_value,
        'personaopera': personaopera,

    }

    return render(request, template_name, context)


class abmAlta(View):
    template_name = 'sistema/abmAlta.html'
    def get_context_data(self, **kwargs):

        app_name = self.kwargs.get('app_name')
        model_name = self.kwargs.get('model_name')
        form_name = self.kwargs.get('form_name')
        model = apps.get_model(app_name, model_name)
        form_cls = importar_formulario(app_name, form_name)

        padre = self.request.GET.get('padre')
        field_name = self.request.GET.get('field_name')
        field_value = self.request.GET.get('field_value')
        personaopera = self.request.GET.get('personaopera')

        titulo = 'Insertar ' + model._meta.verbose_name
        form = form_cls()
        if 'id' in self.request.GET:
            form = form_cls(instance=model.objects.get(id=self.request.GET['id']))
            titulo = 'Editar ' + model._meta.verbose_name
        context = {
            'titulo': titulo,
            'form': form,
            'app_name': app_name,
            'model_name': model_name,
            'form_name': form_name,
            'padre': padre,
            'field_name': field_name,
            'field_value': field_value,
            'personaopera': personaopera,
        }
        return context
    def get(self, request, *args, **kwargs):
        data = dict()
        data['html_form'] = render_to_string(self.template_name, self.get_context_data(), request=request)
        return JsonResponse(data)
    def post(self, request, *args, **kwargs):
        app_name = self.kwargs.get('app_name')
        model_name = self.kwargs.get('model_name')
        form_name = self.kwargs.get('form_name')
        model = apps.get_model(app_name, model_name)
        form_cls = importar_formulario(app_name, form_name)

        form = form_cls(request.POST, request.FILES)
        nuevo = True
        if 'id' in self.request.POST:
            form = form_cls(request.POST, request.FILES, instance=model.objects.get(id=self.request.POST['id']))
            nuevo = False
        if form.is_valid():
            if nuevo:
                if self.request.POST.get('padre'):
                    form.save(commit=False)
                    setattr(form.instance, self.request.POST['field_name'], self.request.POST['field_value'])
                if self.request.POST.get('personaopera'):
                    if self.request.POST.get('personaopera')=='user':
                        form.instance.personaopera = request.user
            form.save()
            data = dict()
            data['resultado'] = "OK"
            return JsonResponse(data)
        else:
            data = dict()
            data['resultado'] = str(form.errors)
            return JsonResponse(data)


class abmEliminar(View):
    def get(self, request, *args, **kwargs):
        app_name = self.kwargs.get('app_name')
        model_name = self.kwargs.get('model_name')
        model = apps.get_model(app_name, model_name)
        model.objects.filter(id=request.GET['id']).delete()
        data = dict()
        data['html_form'] = "OK"
        return JsonResponse(data)
    