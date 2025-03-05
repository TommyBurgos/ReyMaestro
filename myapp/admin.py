from django.contrib import admin

# Register your models here.



# Personalización del panel de administración para asignar profesores
from django.contrib import admin

class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'profesor', 'estado', 'nivel_dificultad')
    list_filter = ('estado', 'nivel_dificultad')
    search_fields = ('titulo', 'profesor__username')
    autocomplete_fields = ['profesor']
