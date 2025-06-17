from django.contrib import admin
from .models import User, Rol, TipoUsuario, Curso,Contenido, Escuela
# Register your models here.

admin.site.register(User)
admin.site.register(Rol)
admin.site.register(TipoUsuario)
admin.site.register(Curso)
admin.site.register(Contenido)
admin.site.register(Escuela)
