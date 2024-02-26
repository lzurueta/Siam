from django.contrib import admin

from sistema.models import Profile, MenuGrupo, Ayuda


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'foto')


admin.site.register(Profile, ProfileAdmin)


class MenuGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo', 'nombre', 'url')


admin.site.register(MenuGrupo, MenuGrupoAdmin)


class AyudaAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo', 'nombre', 'url')


admin.site.register(Ayuda, AyudaAdmin)