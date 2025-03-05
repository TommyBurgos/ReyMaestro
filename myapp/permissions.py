from django.contrib.auth.decorators import user_passes_test

# Verifica si el usuario es administrador
def es_administrador(user):
    return user.is_authenticated and user.rol.nombre == 'Administrador'

# Decorador para vistas protegidas
def administrador_required(view_func):
    decorated_view_func = user_passes_test(es_administrador)(view_func)
    return decorated_view_func
