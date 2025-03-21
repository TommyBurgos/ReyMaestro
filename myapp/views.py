from django.shortcuts import render, HttpResponse
from django.contrib.auth import login, logout, authenticate
from user.models import User, Rol, TipoUsuario
from django.db.models import Q
from django.middleware.csrf import rotate_token
import re

from .permissions import role_required


#FUNCIONES ADICIONALES

# Create your views here.
def inicio(request):
    return render(request, 'inicio/index.html')

@role_required('Administrador')
def inicioAdmin(request):
    user = request.user
    imgPerfil=user.imgPerfil
    # 1. Cantidad de usuarios cuyo rol es igual a 2
    cantidad_usuarios_docentes = User.objects.filter(rol__id=2).count()
    cantidad_usuarios_alumnos = User.objects.filter(rol__id=3).count()
    context = {
        'cantidad_usuarios_docentes': cantidad_usuarios_docentes, 
        'cantidad_usuarios_alumnos':cantidad_usuarios_alumnos,               
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }    
    return render(request, 'usAdmin/index.html', context)


def registroUser(request):
    return render(request, 'inicio/registro.html')

def accesoDenegado(request):
    return render(request, 'generales/accesoDenegado.html')

@role_required('Estudiante')
def inicioEstudiante(request):
    return render(request, 'estudiante/index.html')


def inicioDocente(request):
    return render(request, 'docente/index.html')


def signout(request):
    logout(request)
    rotate_token(request)  # Gira el token CSRF para la nueva sesión
    return redirect('inicio')

from django.contrib.auth import login
from django.shortcuts import redirect

def registroExitoso(request):
    if request.method == 'POST':
        print(request.POST)
        if request.POST['password'] == request.POST['confirmPassword']:
            try:
                password = request.POST.get('password')
                email = request.POST.get('email')
                
                # Validaciones
                if len(password) < 8 or not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
                    return HttpResponse('La contraseña debe tener al menos 8 caracteres y contener letras y números.')

                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    return HttpResponse('El formato del correo electrónico no es válido.')
                
                # Crear usuario
                user = User.objects.create_user(
                    username=email,  # Usa el correo como username
                    email=email,
                    password=password,
                    first_name=request.POST['firstName'],
                    last_name=request.POST['lastName']
                )
                print('***INICIO***')
                # Si quieres asignar rol por defecto
                rol_estudiante = Rol.objects.get(nombre='Estudiante')
                print(rol_estudiante)
                user.rol = rol_estudiante
                print(user.rol)
                tipo_gratis= TipoUsuario.objects.get(nombre='De prueba Gratuita')
                user.tipo_usuario=tipo_gratis
                print(user.tipo_usuario)
                user.save()
                print('***FIN***')
                login(request, user)
                print("Usuario creado y logueado exitosamente.")
                
                return redirect('inicio')  # O la vista que tengas definida
            except Exception as e:
                print(f"❌ Error al crear el usuario: {e}")
                return HttpResponse('Ocurrió un error al crear el usuario.')
        else:
            return HttpResponse('Las contraseñas no coinciden.')
    return HttpResponse('Método no permitido')



def custom_login(request):
    print("entre a la funcion custom")
    if request.method == "POST":  
        print("Estoy en post")      
        user = authenticate(request, username=request.POST['email'], password= request.POST
        ['password'])
        print(user)
        print("Ya autentique el usuario")
        print(user is not None)
        if user is not None:            
            login(request, user)
            print("Loguie al usuario")
            rol = user.rol_id  # Asignar rol después de la autenticación   
            print(rol)         
            if rol == 1:
                print("Ingrese al rol 1")
                return redirect('dashboard-adm')
            elif rol == 2:
                return redirect('dashboard-adm')
            elif rol == 3:
                return redirect('student_dashboard')
        else:
            # Manejar error de autenticación
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return redirect('inicio')


#USO DE OPENAI
import os
import openai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: La API Key de OpenAI no está configurada. Asegúrate de definirla en las variables de entorno.")

# Configurar el cliente OpenAI con la API Key
client = openai.OpenAI(api_key=api_key)

@csrf_exempt
def chatbot_response(request):
    if request.method == "GET":
        return JsonResponse({"message": "La API está funcionando. Usa POST para enviar mensajes."})

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  # Decodifica correctamente el JSON
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "El mensaje está vacío"}, status=400)

            contexto = """
            Esta es una academia de ajedrez. Actualmente ofrecemos los siguientes cursos: Nivel ADC, intermedio, avanzado y Master.
            También tenemos estas promociones activas: $20 el curso de ADC y los demás cursos valen $25.
            Responde a los usuarios con información sobre los cursos y promociones cuando lo pregunten.
            Actualmente estamos trabajando en una nueva plataforma la cual permitirá a los usuarios acceder a cursos pregrabados con su usuario y contraseña.
            Para los cursos de ADC los horarios son los lunes y miércoles de 14:00 a 15:00.
            Para los cursos de intermedio los horarios son los lunes y miércoles de 16:00 a 17:00.
            Para los cursos Avanzando los horarios son los martes y jueves de 14:00 a 15:00.
            Para los cursos Master los horarios son los martes y jueves de 17:00 a 18:00.
            TODOS LOS CURSOS COMPITEN ENTRE SÍ EN LOS TORNEOS LOS DÍAS VIERNES. El estudiante puede unirse en el horario que desee, existe horario de 14:30 a 15:30 y de 18:00 a 19:00.             
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": contexto},
                    {"role": "user", "content": user_message},
                ]
            )

            reply = response.choices[0].message.content
            return JsonResponse({"reply": reply})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error al decodificar JSON. Asegúrate de enviar un cuerpo JSON válido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
