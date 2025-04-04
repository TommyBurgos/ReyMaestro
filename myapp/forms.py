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
            'is_active': 'Estado del usuario'

        }
        widgets = {
            'is_active': forms.Select(choices=[(1, 'Activo'), (0, 'Inactivo')])
        }
