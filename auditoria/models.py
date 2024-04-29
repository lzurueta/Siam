from django.contrib.auth.models import User, Group
from django.db import models
from sistema.models import MenuGrupo


class Auditoria(models.Model):
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.CASCADE)
    grupo = models.ForeignKey(Group, verbose_name='Grupo', on_delete=models.CASCADE, blank=True, null=True)
    title = models.TextField(max_length=200, verbose_name='Titulo')
    description = models.TextField(max_length=800, verbose_name='Texto')
    detail = models.TextField(max_length=800, verbose_name='Detalle auxiliar')
    create_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name="Fecha de Creacion")

    def __str__(self):
        return self.title