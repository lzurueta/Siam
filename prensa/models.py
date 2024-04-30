from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import CASCADE

class Medio(models.Model):
    nombre = models.CharField(max_length=150, null=True, blank=True, verbose_name="nombre")
    def __str__(self):
        return self.nombre

class Reparticion(models.Model):
    nombre = models.CharField(max_length=150, null=True, blank=True, verbose_name="nombre")
    def __str__(self):
        return self.nombre


class Contrato(models.Model):

    OPCIONES = (
        ('P', 'PENDIENTE'),
        ('A', 'AUTORIZADO'),
        ('D', 'DENEGADO')
    )

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    proveedor_rs = models.CharField(max_length=300, null=True, blank=True, verbose_name="Proveedor Razón Social")
    proveedor_cuit = models.BigIntegerField(null=True, blank=True, verbose_name="Proveedor Cuit")
    medio = models.ForeignKey(Medio, on_delete=models.CASCADE, verbose_name='Medio')
    programa = models.CharField(max_length=150, null=True, blank=True, verbose_name="Programa")
    reparticion = models.ForeignKey(Reparticion, on_delete=models.CASCADE, verbose_name='Reparticion')
    monto = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=0.00, blank=False, verbose_name="Monto")
    fechaInicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    fechaFin = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")
    create_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name="Fecha de Creacion")
    update_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Modificacion")
    status = models.CharField(max_length=10, default='P', choices=OPCIONES, verbose_name="Estado")
    def __str__(self):
        return self.programa

    class Meta:
        verbose_name = u"Prensa"
        verbose_name_plural = u"Prensa"
        permissions = (("admin_prensa", "Admin  de Prensa"),)