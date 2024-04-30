from django.contrib import admin
from prensa.models import Medio, Reparticion, Contrato

admin.site.register(Medio)

admin.site.register(Reparticion)

class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'proveedor_rs', 'proveedor_cuit')


admin.site.register(Contrato, ContratoAdmin)

