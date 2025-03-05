from django.shortcuts import render, HttpResponse

#FUNCIONES ADICIONALES

# Create your views here.
def inicio(request):
    return render(request, 'inicio/index.html')

def inicioAdmin(request):
    return render(request, 'usAdmin/index.html')

def registroUser(request):
    return render(request, 'inicio/registro.html')

def inicioEstudiante(request):
    return render(request, 'estudiante/index.html')