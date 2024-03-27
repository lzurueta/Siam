from django.contrib.auth.models import User, Group
from django.db import models

# Create your models here.

Group.add_to_class('home', models.CharField(max_length=150, null=True, blank=True, verbose_name="Home"))
Group.add_to_class('icon', models.CharField(max_length=150, null=True, blank=True, verbose_name="Icono"))

class Profile(models.Model):
    OPCIONES = (
        ('T', 'TITULAR'),
        ('R', 'RESPONSABLE'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150, null=False, blank=True)
    nombreResponsable = models.CharField(max_length=150, null=False, blank=True)
    apellidoResponsable = models.CharField(max_length=150, null=False, blank=True)
    dni = models.IntegerField(null=True, default=None)
    direccion = models.CharField(max_length=150, null=False, blank=True)
    caracter = models.CharField(max_length=10, choices=OPCIONES)
    email = models.EmailField(null=False, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    foto = models.ImageField(null=True, blank=True, upload_to='sistema/profile_images')
    create_at = models.DateTimeField(auto_now_add=True)
    activate_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    disabled_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    def __str__(self):
        return self.user.username


class MenuGrupo(models.Model):
    grupo = models.ForeignKey(Group, verbose_name='Grupo', on_delete=models.CASCADE)
    url = models.CharField(max_length=150, null=True, blank=True, verbose_name="url")
    nombre = models.CharField(max_length=150, null=True, blank=True, verbose_name="nombre")
    orden = models.IntegerField(null=False, default=0)
    def __str__(self):
        return self.grupo.name + ' ' + self.nombre


class Ayuda(models.Model):
    grupo = models.ForeignKey(Group, verbose_name='Grupo', on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=150, null=True, blank=True, verbose_name="nombre")
    descripcion = models.CharField(max_length=10000, null=True, blank=True, verbose_name="Descripción")
    url = models.CharField(max_length=150, null=True, blank=True, verbose_name="url")

    def __str__(self):
        return self.nombre

