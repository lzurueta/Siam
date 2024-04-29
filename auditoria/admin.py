from django.contrib import admin
from auditoria.models import Auditoria
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('user', 'grupo', 'title', 'description', 'detail', 'user', 'create_at')

admin.site.register(Auditoria, AuditoriaAdmin)
