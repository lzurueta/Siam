from django import forms
from django.contrib.auth.models import User
from sistema.models import Profile
from .models import Medio, Reparticion
class registroContrato(forms.Form):

    usuarios_activos = Profile.objects.filter(user__is_active=True).values_list('user__id', 'user__username', 'user__first_name')
    OPCIONES = [(usuario[0], (usuario[1]+' - '+usuario[2])) for usuario in usuarios_activos]

    medios = Medio.objects.values_list('id', 'nombre')
    OPCIONES_MEDIOS = [(medio[0], medio[1]) for medio in medios]

    reparticiones = Reparticion.objects.values_list('id', 'nombre')
    OPCIONES_REP = [(reparticion[0], reparticion[1]) for reparticion in reparticiones]

    usuario = forms.ChoiceField(choices=OPCIONES, label="Proveedor", widget=forms.Select(attrs={
        'placeholder': 'Proveedor',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
    }))

    medio = forms.ChoiceField(choices=OPCIONES_MEDIOS, label="Medio", widget=forms.Select(attrs={
        'placeholder': 'Medio',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
    }))

    programa = forms.CharField(required=True, label="Programa", widget=forms.TextInput(attrs={
        'placeholder': '',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control'
    }))

    reparticion = forms.ChoiceField(choices=OPCIONES_REP, label="Reparticion", widget=forms.Select(attrs={
        'placeholder': '',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control select2',
    }))

    monto = forms.DecimalField(required=True, label="Monto ($ 0000.00)", decimal_places=2, widget=forms.NumberInput(attrs={
        'placeholder': '',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
    }))

    fecha_inicio = forms.DateField(required=True, label="Fecha Inicio", widget=forms.DateInput(attrs={
        'placeholder': '',
        'autocomplete': 'off',
        'type': 'date',
        'required': True,
        'class': 'form-control',
    }))

    fecha_fin = forms.DateField(required=True, label="Fecha Fin", widget=forms.DateInput(attrs={
        'placeholder': 'Fecha Fin',
        'autocomplete': 'off',
        'type': 'date',
        'required': True,
        'class': 'form-control',
    }))