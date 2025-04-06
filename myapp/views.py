from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from user.models import User, Rol, TipoUsuario
from django.db.models import Q
from django.middleware.csrf import rotate_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET

from django.views.decorators.csrf import csrf_exempt

import re
import requests

from .permissions import role_required
from django.core.paginator import Paginator
from .forms import UsuarioForm  # Importa el form
from django.conf import settings

from django.contrib import messages


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

@role_required('Administrador')
def detalleUsuarios(request):
    user = request.user
    usuarios = User.objects.all().order_by('-date_joined')
    imgPerfil=user.imgPerfil
    busqueda = request.GET.get("buscar")
    if busqueda:
        usuarios = User.objects.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        ).distinct()
        print("entre al if de busqueda")
    print("LISTADO DE USUARIOS")
    print(usuarios)

        # Paginación — debe ir después de filtrar los usuarios
    paginator = Paginator(usuarios, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # 1. Cantidad de usuarios cuyo rol es igual a 2    
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,  
        'usuarios':page_obj      
    }
    return render(request, 'usAdmin/detalleAlumnos.html', context)


def ver_o_editar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    # lógica para mostrar o editar
    form = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)
    user = request.user
    imgPerfil=user.imgPerfil
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('detalleUsuarios-adm')  # O la URL que tengas como resumen
    context = {
        'imgPerfil': imgPerfil, 
        'form': form,
        'usuario': usuario,
    }
    return render(request, 'usAdmin/verOeditarUser.html',context)


@role_required('Administrador')
@login_required
def resetear_contrasena(request, id):
    usuario = get_object_or_404(User, id=id)
    
    return redirect('detalle_usuarios')

def resetContra_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    # lógica para mostrar o editar
    nueva_contrasena = "12345678"
    usuario.set_password(nueva_contrasena)  # Cambia la contraseña de forma segura
    usuario.save()
    messages.success(request, f"La contraseña del usuario '{usuario.username}' ha sido reseteada con éxito.")
    return redirect('detalleUsuarios-adm')



@role_required('Administrador')
def detalleCursos(request):
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }
    return render(request, 'usAdmin/detalleCursos.html', context)

@role_required('Administrador')
def detallePagos(request):
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }
    return render(request, 'usAdmin/detallePagos.html', context)

@role_required('Administrador')
def detalleReportes(request):
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }
    return render(request, 'usAdmin/detalleReportes.html', context)

@role_required('Administrador')
def configuracionAdmin(request):
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }
    return render(request, 'usAdmin/configuracion.html', context)

def jugar_vs_computadora(request):
    token = settings.LICHESS_API_TOKEN

    url = 'https://lichess.org/api/challenge/ai'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'level': 3,
        'color': 'random',
        'clock.limit': 300,
        'clock.increment': 0
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code in [200, 201]:
        game_url = f"https://lichess.org/{response.json()['id']}"
        return redirect(game_url)
    else:
        print("Error al crear desafío:")
        print("Código de estado:", response.status_code)
        print("Respuesta:", response.text)
        return redirect('accesoDenegado')



@require_GET
def obtener_estado_partida(request, game_id):
    url = f'https://lichess.org/api/board/game/stream/{game_id}'
    headers = {
        'Authorization': f'Bearer {settings.LICHESS_API_TOKEN}',
        'Accept': 'application/x-ndjson'
    }

    with requests.get(url, headers=headers, stream=True) as response:
        if response.status_code != 200:
            return JsonResponse({'error': 'No se pudo obtener el estado del juego'}, status=400)

        # Obtenemos el último estado
        lines = response.iter_lines()
        for line in lines:
            if line:
                data = json.loads(line.decode('utf-8'))
                if 'state' in data:
                    return JsonResponse(data['state'])

        

@role_required('Administrador')
def soporteAdmin(request):
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,        
    }
    return render(request, 'usAdmin/soporte.html', context)

def ajedrez_vs_ia(request):
    return render(request, 'usAdmin/tablero_vs_ia.html')

def crear_partida_ia(request):
    token = settings.LICHESS_API_TOKEN
    url = 'https://lichess.org/api/challenge/ai'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'level': 3,
        'color': 'white',
        'clock.limit': 300,
        'clock.increment': 0
    }
    response = requests.post(url, headers=headers, data=data)
    return JsonResponse(response.json(), safe=False)



@csrf_exempt
@require_POST
def enviar_movimiento(request):
    try:
        data = json.loads(request.body)
        game_id = data.get('gameId')
        move = data.get('move')

        print("🔁 Movimiento recibido:")
        print("Game ID:", game_id)
        print("Movimiento:", move)

        url = f'https://lichess.org/api/board/game/{game_id}/move/{move}'
        headers = {
            'Authorization': f'Bearer {settings.LICHESS_API_TOKEN}'
        }

        response = requests.post(url, headers=headers)

        print("📩 Respuesta de Lichess:", response.status_code, response.text)

        if response.status_code in [200, 201]:
            return JsonResponse({'status': 'ok', 'lichess': response.json()})
        else:
            return JsonResponse({
                'status': 'error',
                'code': response.status_code,
                'response': response.text
            }, status=400)
    except Exception as e:
        print("❌ Error procesando movimiento:", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def editarPerfil(request):
    user = request.user
    # lógica para mostrar o editar
    form = UsuarioForm(request.POST or None, request.FILES or None, instance=user)    
    imgPerfil=user.imgPerfil
    print("Saber si entra o no al if: ",request.method == 'POST' and form.is_valid())
    if request.method == 'POST' and form.is_valid():
        print("Archivos recibidos:", request.FILES)
        print("Datos del formulario:", request.POST)
        form.save()
        return redirect('detalleUsuarios-adm')
    context = {
        'imgPerfil': imgPerfil, 
        'form': form,
        'usuario': user,
    }
    return render(request, 'usAdmin/editarPerfil.html',context)

from django.contrib.auth import update_session_auth_hash

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        user = request.user
        actual = request.POST.get('password_actual')
        nueva = request.POST.get('nueva_password')
        repetir = request.POST.get('repetir_password')

        if not user.check_password(actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif nueva != repetir:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
        else:
            user.set_password(nueva)
            user.save()
            update_session_auth_hash(request, user)  # Esta línea evita el logout
            messages.success(request, '¡Tu contraseña ha sido cambiada con éxito!')
            return redirect('editarPerfil-adm')

    return redirect('editarPerfil-adm')



def registroUser(request):
    return render(request, 'inicio/registro.html')

def accesoDenegado(request):
    return render(request, 'generales/accesoDenegado.html')

@role_required('Estudiante')
def inicioEstudiante(request):
    return render(request, 'usEstudiante/index.html')

@role_required('Estudiante')
def chatEstudiante(request):
    return render(request, 'usEstudiante/chat.html')

@role_required('Estudiante')
def notificacionesEstudiante(request):
    return render(request, 'usEstudiante/notificaciones.html')

@role_required('Estudiante')
def progresoEstudiante(request):
    return render(request, 'usEstudiante/progreso.html')

@role_required('Estudiante')
def rutasEstudiante(request):
    return render(request, 'usEstudiante/rutas.html')

@role_required('Estudiante')
def cursosEstudiante(request):
    return render(request, 'usEstudiante/cursos.html')

@role_required('Estudiante')
def detalleCursoEstudiante(request):
    return render(request, 'usEstudiante/detalleCurso.html')

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
            return render(request, 'generales/accesoDenegado.html', {'error': 'Credenciales inválidas'})
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
