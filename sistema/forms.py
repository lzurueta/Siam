from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
import re


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class registroUsuario(forms.Form):

    OPCIONES = (
        ('T', 'TITULAR'),
        ('R', 'RESPONSABLE'),
    )

    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'CUIL/CUIT',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
        'type': 'number'
    }))

    nombre = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Razón Social',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control'
    }))

    nombreResponsable = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Nombre Responsable',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control'
    }))

    apellidoResponsable = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Apellido Responsable',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control'
    }))

    dni = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'DNI',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
        'type': 'number'
    }))

    caracter = forms.ChoiceField(choices=OPCIONES, widget=forms.Select(attrs={
        'placeholder': 'Carácter',
        'autocomplete': 'off',
        'required': True,
        'class': 'form-control',
    }))

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Mail',
        'required': True
    }))
    direccion = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Dirección y C.P.',
        'required': True
    }))
    telefono = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'number',
        'autocomplete': 'off',
        'placeholder': 'Celular',
        'required': False,
        'max_length': 20
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Contraseña',
        'required': True
    }))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'placeholder': 'Repetir Contraseña',
        'required': True
    }))


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('El número de CUIT ya se encuentra registrado.')
            print('El número de CUIT ya se encuentra registrado.')
        return username

    def clean_email(self):
        correo = self.cleaned_data.get('email')
        if User.objects.filter(email=correo).exists():
         raise forms.ValidationError('El mail ya se encuentra registrado.')
        return correo

    def clean_password2(self):
            password = self.cleaned_data.get('password')
            password2 = self.cleaned_data.get('password2')

            if password != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            else:
                if validar_contrasena(password) and len(password) >= 12:
                    return password2
                else:
                    raise forms.ValidationError(
                        'La contraseña debe tener al menos 12 caracteres, al menos una mayúscula, una minúsculas, un número y un simbolo especial.')


def validar_contrasena(contrasena):
    # Verificar si la contraseña contiene al menos una letra mayúscula
    if not re.search(r'[A-Z]', contrasena):
        return False

    # Verificar si la contraseña contiene al menos una letra minúscula
    if not re.search(r'[a-z]', contrasena):
        return False

    # Verificar si la contraseña contiene al menos un número
    if not re.search(r'\d', contrasena):
        return False

    # Verificar si la contraseña contiene al menos un símbolo
    if not re.search(r'[\W_]', contrasena):
        return False

    # Verificar la longitud de la contraseña (opcional)
    if len(contrasena) < 8:
        return False

    return True

