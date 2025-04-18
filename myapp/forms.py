# usAdmin/forms.py

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'imgPerfil', 'is_active']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'imgPerfil': 'Foto de perfil',
            'is_active': 'Estado del usuario',
            'password':'opciones de contraseña'

        }
        widgets = {
            'is_active': forms.Select(choices=[(1, 'Activo'), (0, 'Inactivo')])
        }

from user.models import Curso

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = [
            'titulo',
            'descripcion',
            'fecha_publicacion',
            'destacado',
            'estado',
            'nivel_dificultad'
        ]
        widgets = {
            'fecha_publicacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        