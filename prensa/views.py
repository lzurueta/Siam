from django.shortcuts import render
from django.views import View
from sistema.functions import traerIndex
from django.http import JsonResponse, HttpResponse

from .forms import registroContrato

from django.db.models import F, Func, Value, CharField

from .models import Contrato, Medio, Reparticion

from django.contrib.auth.models import User, Group

from sistema.functions import generate_pdf, insertAuditoria, traerPermisos

from sistema.models import Profile

from auditoria.models import Auditoria

from django.db.models import Sum, Count, Q

from datetime import timedelta

import locale

# Create your views here.

class contratos(View):
    template_name = 'prensa/contratos.html'

    def get_context_data(self, **kwargs):

        form = registroContrato()

        if 'prensa.admin_prensa' in traerPermisos(self.request):
            admin = True
        else:
            admin = False

        context = {
            'titulo': "Contratos",
            'index': traerIndex(self.request),
            'form': form,
            'admin': admin
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


class contratos_ajax(View):
    """COMPLETAR DATOS DE TABLA DE CONTRATOS"""
    def post(self, request):

        nro = request.POST.get('nro') or 0

        contrato = Contrato.objects.filter(pk=nro).annotate(
        monto_formateado=Func( F('monto'), Value('9G999G999G999D99'), function='TO_CHAR', output_field=CharField()),
        fechaInicio_formateada=Func(F('fechaInicio'), Value('DD-MM-YYYY'), function='TO_CHAR', output_field=CharField()),
        fechaFin_formateada=Func(F('fechaFin'), Value('DD-MM-YYYY'), function='TO_CHAR', output_field=CharField())
        ).values(
        'id',
        'user__profile__nombre',
        'user__username',
        'medio__nombre',
        'proveedor_rs',
        'proveedor_cuit',
        'programa',
        'monto_formateado',
        'reparticion__nombre',
        'fechaInicio_formateada',
        'fechaFin_formateada',
        'status'
        )

        title = 'CONSULTA DE CONTRATO'
        description = 'Consulta de contrato N° ' + str(request.POST.get('nro'))
        detail = '-'

        if request.POST.get('nro'):
            insertAuditoria(request.user, 'Prensa', title, description, detail)

        data = list(contrato)
        return JsonResponse(data, safe=False)

def guardarFormContrato(request):
    """DAR DE ALTA NUEVO CONTRATO"""
    form = registroContrato(request.POST or None)
    if request.method == "POST" and form.is_valid():

        usuario_id = form.cleaned_data.get('usuario')
        if usuario_id:
            proveedor = User.objects.filter(id=usuario_id).first()
        else:
            proveedor = None

        proveedor_rs = form.cleaned_data.get('proveedor_rs')
        proveedor_cuit = form.cleaned_data.get('proveedor_cuit')
        medio = Medio.objects.filter(id=form.cleaned_data.get('medio')).first()
        programa = form.cleaned_data.get('programa')
        reparticion = Reparticion.objects.filter(id=form.cleaned_data.get('reparticion')).first()
        monto = form.cleaned_data.get('monto')
        fechaInicio = form.cleaned_data.get('fecha_inicio')
        fechaFin = form.cleaned_data.get('fecha_fin')

        contrato = Contrato.objects.create(
            user=proveedor,
            proveedor_rs=proveedor_rs,
            proveedor_cuit=proveedor_cuit,
            medio=medio,
            programa=programa,
            reparticion=reparticion,
            monto=monto,
            fechaInicio=fechaInicio,
            fechaFin=fechaFin,
            status='P'
        )

        idNuevoContrato = Contrato.objects.latest('id').id

        grupo = 'Prensa'
        title = 'ALTA DE CONTRATO'
        description = 'Alta de contrato N° '+str(idNuevoContrato)
        detail = 'Id: '+str(idNuevoContrato)

        insertAuditoria(request.user, grupo, title, description, detail)

        return JsonResponse({'contrato': idNuevoContrato})

    else:
        errors = dict(form.errors)
        return JsonResponse({'errors': errors})

def contrato_pdf(request):
    """ IMPRESOR DE CONTRATO """
    template_name = 'prensa/contrato_pdf.html'

    id = request.POST.get('id')
    contrato = Contrato.objects.get(id = id)
    if contrato.user:
        profile = Profile.objects.get(user = contrato.user)
    else:
        profile = None
    context = {
        'contrato': contrato,
        'profile': profile
    }

    return generate_pdf(request, template_name, context)

def autorizar_contrato(request):
    """AUTORIZAR CONTRATO"""
    contrato = Contrato.objects.get(pk=request.POST.get('id'))
    contrato.status = 'A'
    contrato.save()

    grupo = 'Prensa'
    title = 'AUTORIZACIÓN DE CONTRATO'
    description = 'Autorización de contrato N° ' + str(request.POST.get('id'))
    detail = 'Estado Anterior: P'

    insertAuditoria(request.user, grupo, title, description, detail)

    return HttpResponse()

def denegar_contrato(request):
    """DENEGAR CONTRATO"""
    contrato = Contrato.objects.get(pk=request.POST.get('id'))
    contrato.status = 'D'
    contrato.save()

    grupo = 'Prensa'
    title = 'DENGACIÓN DE CONTRATO'
    description = 'Denegación de contrato N° ' + str(request.POST.get('id'))
    detail = 'Estado Anterior: P'

    insertAuditoria(request.user, grupo, title, description, detail)

    return HttpResponse()

def datos_graficos(request):
    """DATOS PARA GRAFICOS"""

    anio = request.POST.get('anio')

    cantidad_proveedores = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A',user__isnull=False).values('user').distinct().count()
    cantidad_medio = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('medio').distinct().count()
    cantidad_reparticion = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('reparticion').distinct().count()
    monto_acumulado = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').distinct().aggregate(Sum('monto'))['monto__sum']

    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    if monto_acumulado:
        monto_formateado = locale.currency(monto_acumulado, grouping=True, symbol=False)
    else:
        monto_formateado = '0,00'

    proveedores_top_10CP = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A', user__isnull=False).values('user__first_name').annotate(total_contratos=Count('id')).order_by('-total_contratos')[:10]

    top_10_arrayCP = []

    for proveedor in proveedores_top_10CP:
        top_10_arrayCP.append({'y': proveedor['user__first_name'], 'a': proveedor['total_contratos']})


    proveedores_top_10CR = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('reparticion__nombre').annotate(total_contratos=Count('id')).order_by('-total_contratos')[:10]

    top_10_arrayCR = []

    for repartocion in proveedores_top_10CR:
        top_10_arrayCR.append({'y': repartocion['reparticion__nombre'], 'a': repartocion['total_contratos']})

    proveedores_top_10CM = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('medio__nombre').annotate(total_contratos=Count('id')).order_by('-total_contratos')[:10]

    top_10_arrayCM = []

    for medio in proveedores_top_10CM:
        top_10_arrayCM.append({'y': medio['medio__nombre'], 'a': medio['total_contratos']})

    proveedores_top_10MP = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A', user__isnull=False).values('user__first_name').annotate(monto_total=Sum('monto')).order_by('-monto_total')[:10]

    top_10_arrayMP = []

    for proveedor in proveedores_top_10MP:
        top_10_arrayMP.append({'y': proveedor['user__first_name'], 'a': proveedor['monto_total']})


    repartocion_top_10MR = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('reparticion__nombre').annotate(monto_total=Sum('monto')).order_by('-monto_total')[:10]

    top_10_arrayMR = []

    for repartocion in repartocion_top_10MR:
        top_10_arrayMR.append({'y': repartocion['reparticion__nombre'], 'a': repartocion['monto_total']})


    medio_top_10MM = Contrato.objects.filter(Q(fechaInicio__year=anio) | Q(fechaFin__year=anio), status='A').values('medio__nombre').annotate(monto_total=Sum('monto')).order_by('-monto_total')[:10]

    top_10_arrayMM = []

    for medio in medio_top_10MM:
        top_10_arrayMM.append({'y': medio['medio__nombre'], 'a': medio['monto_total']})

    data = {
        "cantidad_proveedores" : cantidad_proveedores,
        "cantidad_medio" : cantidad_medio,
        "cantidad_reparticion" : cantidad_reparticion,
        "monto_acumulado" : monto_formateado,
        "top_10_arrayCP": top_10_arrayCP,
        "top_10_arrayCR": top_10_arrayCR,
        "top_10_arrayCM" : top_10_arrayCM,
        "top_10_arrayMP" : top_10_arrayMP,
        "top_10_arrayMR" : top_10_arrayMR,
        "top_10_arrayMM" : top_10_arrayMM
    }

    return JsonResponse(data, safe=False)


class auditoria(View):
    template_name = 'prensa/contratos_auditoria.html'

    def get_context_data(self, **kwargs):

        usuarios = User.objects.filter(is_active=True)
        context = {
            'titulo': "Auditoría",
            'index': traerIndex(self.request),
            'usuarios': usuarios
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

class auditoria_ajax(View):
    """COMPLETAR DATOS DE TABLA DE AUDITORIA"""
    def post(self, request):

        titulo = request.POST.get('titulo')
        desc = request.POST.get('desc')
        detalle = request.POST.get('detalle')
        usuario = request.POST.get('usuario')
        desde = ''

        if request.POST.get('desde') != '':
            desde = request.POST.get('desde')+" 00:00:00"

        hasta = ''
        if request.POST.get('hasta') != '':
            hasta = request.POST.get('hasta')+" 23:59:59"

        auditoria = Auditoria.objects.filter(grupo__name='Prensa').annotate(
        fecha_formateada=Func(
        F('create_at') - timedelta(hours=3),  # Sumar 3 horas
        Value('DD-MM-YYYY HH24:MI'),  # Formato deseado
        function='TO_CHAR',
        output_field=CharField()
         )
        ).values(
        'title',
        'description',
        'detail',
        'user__first_name',
        'user__last_name',
        'fecha_formateada',
        'create_at',
        )

        if titulo:
            auditoria = auditoria.filter(title__icontains=titulo)

        if desc:
            auditoria = auditoria.filter(description__icontains=desc)

        if detalle:
            auditoria = auditoria.filter(detail__icontains=detalle)

        if usuario:
            auditoria = auditoria.filter(user__pk=usuario)

        if desde:
            auditoria = auditoria.filter(create_at__gte=desde)

        if hasta:
            auditoria = auditoria.filter(create_at__lte=hasta)

        data = list(auditoria)
        return JsonResponse(data, safe=False)
