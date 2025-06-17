from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from user.models import User, Rol, TipoUsuario, Curso, Contenido, Modulo, Leccion, Inscripcion, Curso, Pago, User, ProgresoUsuario, Foro, ComentarioForo, Calificacion
from django.db.models import Q
from django.middleware.csrf import rotate_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET

from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

import re
import requests
import uuid
#LIBRERIAS PARA GENERACIÓN DE REPORTES
import pandas as pd
from reportlab.pdfgen import canvas
from django.utils.timezone import make_aware
from datetime import datetime
from datetime import timedelta




from .permissions import role_required
from django.core.paginator import Paginator
from .forms import UsuarioForm, CursoForm  # Importa el form
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
    # Fecha hace dos semanas
    dos_semanas_atras = timezone.now() - timedelta(weeks=4)
    #Ultimos cursos creados
    cursos = Curso.objects.all().order_by('-fecha_creacion').filter(fecha_creacion__gte=dos_semanas_atras)
    # Usuarios creados en las últimas dos semanas
    usuarios_recientes = User.objects.filter(date_joined__gte=dos_semanas_atras)

    cantidad_usuarios_docentes = User.objects.filter(rol__id=2).count()
    cantidad_usuarios_alumnos = User.objects.filter(rol__id=3).count()
    print(f"Estos son los nuevos usuarios: {usuarios_recientes}")
    print(user.rol_id)    
    context = {
        'cantidad_usuarios_docentes': cantidad_usuarios_docentes, 
        'cantidad_usuarios_alumnos':cantidad_usuarios_alumnos,
        'usuarios_recientes': usuarios_recientes,               
        'imgPerfil': imgPerfil,
        'cursos':cursos,        
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
    cursos = Curso.objects.all().order_by('-fecha_creacion')
    user = request.user
    imgPerfil=user.imgPerfil
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,     
        'cursos':cursos   
    }
    return render(request, 'usAdmin/detalleCursos.html', context)

from .storages_backends import S3VideoStorage

@role_required('Administrador')
@login_required
def crear_curso(request):
    if request.method == 'POST':
        print("INICIANDO LA FUNCIÓN")
        form = CursoForm(request.POST)
        video_file = request.FILES.get('video')
        titulo_video = request.POST.get('titulo', '').strip()
        descripcion_video = request.POST.get('descripcionVideo', '').strip()
        print(form.is_valid() and video_file)
        print(form.is_valid())
        print(video_file)        
        print(form)
        print("Antes de los if")
        print(form.is_valid() and video_file)
        print(titulo_video)
        print(video_file.name.endswith(('.mp4', '.webm', '.avi')))
        print(video_file.size > 200 * 1024 * 1024)
        if not titulo_video:
            messages.error(request, "Debes ingresar el título del video.")
            print("En el 1er if")
            return render(request, 'usAdmin/crear_curso.html', {'form': form})

        if not video_file.name.endswith(('.mp4', '.webm', '.avi')):
            messages.error(request, "El formato de video no es válido.")
            print("En el 2do if")
            return render(request, 'usAdmin/crear_curso.html', {'form': form})

        if video_file.size > 200 * 1024 * 1024:  # 200 MB
            messages.error(request, "El video excede el tamaño máximo permitido (200MB).")
            print("En el 3er if")
            return render(request, 'usAdmin/crear_curso.html', {'form': form})

        if form.is_valid() and video_file:
            print("DENTRO, En el 4to if")
            print("Antes de guardar el curso")
            curso = form.save(commit=False)
            curso.profesor = request.user
            curso.save()
            print("Curso Guardado.")

            # Subir video a S3
            ext = video_file.name.split('.')[-1]
            video_nombre = f"videos/{uuid.uuid4()}.{ext}"  # Nombre único
            s3_storage = S3VideoStorage()
            video_path = s3_storage.save(video_nombre, video_file)
            #video_path = default_storage.save(video_nombre, video_file)
            print("Antes de general la URL")
            # Generar URL pública
            video_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{video_path}"
            print(f"Ruta creada {video_url}")
            # Crear contenido asociado al curso
            Contenido.objects.create(
                curso=curso,
                titulo=request.POST.get('tituloVideo'),
                tipo_contenido='video',
                url_contenido=video_url,
                descripcion=request.POST.get('descripcionVideo')
            )

            messages.success(request, "Curso y video creados exitosamente.")
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        print("Estoy en el else")
        form = CursoForm()
    print("Llegue al final de la función")
    return render(request, 'usAdmin/crear_curso.html', {'form': form})

@role_required('Administrador')
@login_required
def eliminar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == 'POST':
        curso.delete()
        messages.success(request, f"Curso '{curso.titulo}' eliminado correctamente.")
        return redirect('listado_cursos')  # o donde estés listando los cursos

    return render(request, 'usAdmin/confirmar_eliminacion.html', {'curso': curso})


from django.db.models import Prefetch

@role_required('Administrador')
@login_required
def listado_cursos(request):
    cursos = Curso.objects.all().order_by('-fecha_creacion')
    return render(request, 'usAdmin/listado_cursos.html', {'cursos': cursos})

@role_required('Administrador')
@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    contenidos = Contenido.objects.filter(curso=curso, tipo_contenido='video')

    return render(request, 'usAdmin/detalle_curso.html', {
        'curso': curso,
        'contenidos': contenidos
    })

@role_required('Administrador')
@login_required
def ver_leccion(request, leccion_id):
    leccion = get_object_or_404(Leccion, id=leccion_id)
    modulo = leccion.modulo
    otras_lecciones = modulo.leccion_set.all().order_by('orden')

    return render(request, 'usAdmin/ver_leccion.html', {
        'leccion': leccion,
        'modulo': modulo,
        'otras_lecciones': otras_lecciones,
    })

from django.utils import timezone

from .storages_backends import S3VideoStorage

@role_required('Administrador')
@login_required
def agregar_contenido(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        tipo = request.POST.get('tipo')
        archivo = request.FILES.get('archivo')
        texto = request.POST.get('texto', '')

        if not titulo or not tipo:
            messages.error(request, "Título y tipo de contenido son obligatorios.")
            return redirect('agregar_contenido', curso_id=curso.id)

        url_contenido = None
        archivo_guardado = None

        if tipo in ['video', 'documento'] and archivo:
            ext = archivo.name.split('.')[-1]
            nombre_unico = f"{tipo}s/{uuid.uuid4()}.{ext}"

            # 🔐 Usar almacenamiento personalizado en S3 solo para videos y documentos
            s3_storage = S3VideoStorage()
            ruta_archivo = s3_storage.save(nombre_unico, archivo)
            url_contenido = s3_storage.url(ruta_archivo)

            # Solo guarda archivo físicamente si es documento
            if tipo == 'documento':
                archivo_guardado = None  # Puedes dejarlo como None si solo usas la URL
            else:
                archivo_guardado = None

        Contenido.objects.create(
            curso=curso,
            titulo=titulo,
            tipo_contenido=tipo,
            url_contenido=url_contenido if tipo != 'texto' else None,
            descripcion=descripcion,
            archivo=archivo_guardado,
            fecha_subida=timezone.now()
        )

        messages.success(request, "Contenido agregado exitosamente.")
        return redirect('detalle_curso', curso_id=curso.id)

    return render(request, 'usAdmin/agregar_contenido.html', {'curso': curso})


@role_required('Administrador')
@login_required
def crear_modulo(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        orden = request.POST.get('orden', 1)

        if not titulo:
            messages.error(request, "El título del módulo es obligatorio.")
            return redirect('crear_modulo', curso_id=curso.id)

        Modulo.objects.create(
            curso=curso,
            titulo=titulo,
            descripcion=descripcion,
            orden=orden
        )
        messages.success(request, "Módulo creado exitosamente.")
        return redirect('detalle_curso', curso_id=curso.id)

    return render(request, 'usAdmin/crear_modulo.html', {'curso': curso})

@role_required('Administrador')
@login_required
def crear_leccion(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion', '').strip()
        archivo = request.FILES.get('archivo')
        imagen = request.FILES.get('imagen')
        orden = request.POST.get('orden', 1)

        if not titulo or not tipo:
            messages.error(request, "Título y tipo de contenido son obligatorios.")
            return redirect('crear_leccion', modulo_id=modulo.id)

        url_contenido = None
        archivo_guardado = None

        if tipo in ['video', 'documento'] and archivo:
            ext = archivo.name.split('.')[-1]
            nombre_archivo = f"{tipo}s/{uuid.uuid4()}.{ext}"
            s3_storage = S3VideoStorage()
            ruta = s3_storage.save(nombre_archivo, archivo)
            url_contenido = s3_storage.url(ruta)

        nueva_leccion = Leccion.objects.create(
            modulo=modulo,
            titulo=titulo,
            tipo_contenido=tipo,
            descripcion=descripcion,
            url_contenido=url_contenido,
            archivo=None,  # Puedes dejar como None si ya guardas solo URL
            imagen=imagen,  # Esto se guarda local en MEDIA_ROOT
            orden=orden
        )

        messages.success(request, "Lección creada correctamente.")
        return redirect('detalle_curso', curso_id=modulo.curso.id)

    return render(request, 'usAdmin/crear_leccion.html', {'modulo': modulo})


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
    cursos = Curso.objects.all().order_by('-fecha_creacion')
    context = {                     
        'imgPerfil': imgPerfil,        
        'usuario':user.username,
        'cursos': cursos      
    }
    return render(request, 'usAdmin/detalleReportes.html', context)

#FUNCIONES PARA GENERAR REPORTES
def preparar_reporte_inscripciones(filtros):
    inscripciones = Inscripcion.objects.filter(**filtros).select_related('usuario', 'curso')
    datos = []
    for inscripcion in inscripciones:
        datos.append({
            'Usuario': inscripcion.usuario.username,
            'Curso': inscripcion.curso.titulo,
            'Fecha de inscripción': inscripcion.fecha_inscripcion.strftime("%d/%m/%Y"),
            'Estado': inscripcion.estado,
            'Progreso': f"{inscripcion.progreso}%",
        })
    return datos

def preparar_reporte_cursos():
    cursos = Curso.objects.all()
    datos = []
    for curso in cursos:
        datos.append({
            'Título': curso.titulo,
            'Profesor': curso.profesor.username,
            'Fecha de creación': curso.fecha_creacion.strftime("%d/%m/%Y"),
            'Estado': curso.estado,
            'Nivel': curso.nivel_dificultad,
        })
    return datos

def preparar_reporte_pagos(filtros):
    pagos = Pago.objects.filter(**filtros).select_related('usuario')
    datos = []
    for pago in pagos:
        datos.append({
            'Usuario': pago.usuario.username,
            'Monto': f"${pago.monto}",
            'Método': pago.metodo_pago,
            'Estado de pago': pago.estado_pago,
            'Fecha de pago': pago.fecha_pago.strftime("%d/%m/%Y"),
        })
    return datos

def preparar_reporte_progreso(filtros):
    progresos = ProgresoUsuario.objects.filter(**filtros).select_related('usuario', 'contenido')
    datos = []
    for progreso in progresos:
        datos.append({
            'Usuario': progreso.usuario.username,
            'Contenido': progreso.contenido.titulo,
            'Completado': 'Sí' if progreso.completado else 'No',
            'Fecha Actualización': progreso.fecha_actualizacion.strftime("%d/%m/%Y"),
        })
    return datos

def preparar_reporte_foros(filtros):
    foros = Foro.objects.all()
    datos = []
    for foro in foros:
        comentarios = ComentarioForo.objects.filter(foro=foro).count()
        datos.append({
            'Curso': foro.curso.titulo,
            'Título del Foro': foro.titulo,
            'Cantidad de Comentarios': comentarios,
            'Fecha de creación': foro.fecha_creacion.strftime("%d/%m/%Y"),
        })
    return datos

def preparar_reporte_calificaciones(filtros):
    calificaciones = Calificacion.objects.select_related('inscripcion', 'contenido')
    datos = []
    for calificacion in calificaciones:
        datos.append({
            'Usuario': calificacion.inscripcion.usuario.username,
            'Curso': calificacion.inscripcion.curso.titulo,
            'Contenido': calificacion.contenido.titulo,
            'Calificación': calificacion.calificacion,
            'Fecha de Calificación': calificacion.fecha_calificacion.strftime("%d/%m/%Y"),
        })
    return datos

##GENERACIÓN DEL PDF
def generar_pdf(datos, nombre_archivo):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"{nombre_archivo}.pdf\"'
    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, f"Reporte: {nombre_archivo.replace('_', ' ').title()}")
    y = 770

    for registro in datos:
        p.setFont("Helvetica", 10)
        for clave, valor in registro.items():
            p.drawString(50, y, f"{clave}: {valor}")
            y -= 15
            if y <= 50:
                p.showPage()
                y = 800
        y -= 10

    p.showPage()
    p.save()
    return response

def generar_excel(datos, nombre_archivo):
    df = pd.DataFrame(datos)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=\"{nombre_archivo}.xlsx\"'
    df.to_excel(response, index=False, engine='openpyxl')
    return response




def generar_reporte(request):
    if request.method == 'GET':
        tipo_reporte = request.GET.get('tipo_reporte')
        formato = request.GET.get('formato')
        curso_id = request.GET.get('curso')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        estado = request.GET.get('estado')

        tipo_reporte = request.GET.get('tipo_reporte')
        formato = request.GET.get('formato')
        if not tipo_reporte or not formato:
            return HttpResponse("Por favor selecciona tipo de reporte y formato.", status=400)

        # Procesar los filtros
        filtros = {}
        if curso_id and curso_id != 'todos':
            filtros['curso_id'] = curso_id

        if fecha_desde:
            filtros['fecha_inscripcion__gte'] = make_aware(datetime.strptime(fecha_desde, "%Y-%m-%d"))
        if fecha_hasta:
            filtros['fecha_inscripcion__lte'] = make_aware(datetime.strptime(fecha_hasta, "%Y-%m-%d"))

        if estado and estado != 'todos':
            filtros['estado'] = estado

        # Preparar datos según tipo de reporte
        if tipo_reporte == 'inscripciones':
            datos = preparar_reporte_inscripciones(filtros)
            nombre_archivo = 'reporte_inscripciones'
        elif tipo_reporte == 'cursos':
            datos = preparar_reporte_cursos()
            nombre_archivo = 'reporte_cursos'
        elif tipo_reporte == 'pagos':
            datos = preparar_reporte_pagos(filtros)
            nombre_archivo = 'reporte_pagos'
        elif tipo_reporte == 'progreso':
            datos = preparar_reporte_progreso(filtros)
            nombre_archivo = 'reporte_progreso'
        elif tipo_reporte == 'foros':
            datos = preparar_reporte_foros(filtros)
            nombre_archivo = 'reporte_foros'
        elif tipo_reporte == 'calificaciones':
            datos = preparar_reporte_calificaciones(filtros)
            nombre_archivo = 'reporte_calificaciones'
        else:
            return HttpResponse("Tipo de reporte no válido.", status=400)

        # Generar PDF o Excel según formato elegido
        if formato == 'pdf':
            return generar_pdf(datos, nombre_archivo)
        elif formato == 'excel':
            return generar_excel(datos, nombre_archivo)
        else:
            return HttpResponse("Formato no válido.", status=400)            

    return redirect('nombre_de_tu_vista_formulario_reportes')  # Cambiar por la vista del formulario


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


#PARA ENVIO DE MENSAJES
from user.models import Mensaje
from .forms import MensajeForm

@login_required
def bandeja_entrada(request):
    mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-fecha_envio')
    return render(request, 'mensajes/mensajeria.html', {'mensajes': mensajes})

@login_required
def enviar_mensaje(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.save()
            return redirect('bandeja_entrada')
    else:
        form = MensajeForm()
    return render(request, 'mensajes/enviar_mensaje.html', {'form': form})

@login_required
def detalle_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)

    # Solo destinatario o remitente pueden ver
    if request.user != mensaje.destinatario and request.user != mensaje.remitente:
        return redirect('bandeja_entrada')

    # Marcar como leído
    if not mensaje.leido and request.user == mensaje.destinatario:
        mensaje.leido = True
        mensaje.save()

    # Manejar respuesta
    if request.method == 'POST':
        contenido_respuesta = request.POST.get('respuesta')
        if contenido_respuesta:
            Mensaje.objects.create(
                remitente=request.user,
                destinatario=mensaje.remitente,
                asunto=f"RE: {mensaje.asunto}",
                contenido=contenido_respuesta
            )
            return redirect('bandeja_entrada')

    return render(request, 'mensajes/detalle_mensaje.html', {'mensaje': mensaje})

@login_required
def mensajes_enviados(request):
    mensajes = Mensaje.objects.filter(remitente=request.user).order_by('-fecha_envio')
    return render(request, 'mensajes/mensajes_enviados.html', {'mensajes': mensajes})



def registroUser(request):
    return render(request, 'inicio/registro.html')

def accesoDenegado(request):
    return render(request, 'generales/accesoDenegado.html')

@role_required('Estudiante')
def inicioEstudiante(request):
    user = request.user
    imgPerfil=user.imgPerfil    
    # 1. Cantidad de usuarios cuyo rol es igual a 2
    # Fecha hace dos semanas    
    #Ultimos cursos creados
    cursos = Curso.objects.all().order_by('-fecha_creacion')
    # Usuarios creados en las últimas dos semanas    
    context = {                   
        'imgPerfil': imgPerfil,
        'cursos':cursos,        
        'usuario':user.username,        
    }    
    return render(request, 'usEstudiante/index.html', context)    

def actualizar_progreso(inscripcion):
    total_contenidos = Contenido.objects.filter(curso=inscripcion.curso).count()
    total_lecciones = Leccion.objects.filter(modulo__curso=inscripcion.curso).count()
    total_items = total_contenidos + total_lecciones

    completados_contenido = ProgresoUsuario.objects.filter(
        usuario=inscripcion.usuario,
        contenido__curso=inscripcion.curso,
        completado=True
    ).count()

    completados_leccion = ProgresoUsuario.objects.filter(
        usuario=inscripcion.usuario,
        leccion__modulo__curso=inscripcion.curso,
        completado=True
    ).count()

    progreso = ((completados_contenido + completados_leccion) / total_items) * 100 if total_items > 0 else 0
    inscripcion.progreso = progreso
    inscripcion.save()


@role_required('Estudiante')
def detalle_curso_Estudiante(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    contenidos = Contenido.objects.filter(curso=curso, tipo_contenido='video')
    inscripcion, creada = Inscripcion.objects.get_or_create(
        usuario=request.user,
        curso=curso,
        defaults={'estado': 'en_progreso'}
    )

    return render(request, 'usEstudiante/detalleCurso.html', {
        'curso': curso,
        'contenidos': contenidos,
        'inscripcion': inscripcion
    })

@role_required('Estudiante')
def ver_leccion_Estudiante(request, leccion_id):
    leccion = get_object_or_404(Leccion, id=leccion_id)
    modulo = leccion.modulo
    curso = modulo.curso
    otras_lecciones = modulo.leccion_set.all().order_by('orden')

    # 1. Registrar progreso de esta lección si no está ya completado
    ProgresoUsuario.objects.get_or_create(
        usuario=request.user,
        leccion=leccion,
        defaults={'completado': True}
    )

    # 2. Asegurar que exista inscripción
    inscripcion, creada = Inscripcion.objects.get_or_create(
        usuario=request.user,
        curso=curso,
        defaults={'estado': 'en_progreso'}
    )

    # 3. Actualizar progreso general del curso
    actualizar_progreso(inscripcion)

    return render(request, 'usEstudiante/detalleCursoLeccion.html', {
        'leccion': leccion,
        'modulo': modulo,
        'otras_lecciones': otras_lecciones,
    })


@role_required('Estudiante')
def chatEstudiante(request):
    return render(request, 'usEstudiante/chat.html')

@role_required('Estudiante')
def notificacionesEstudiante(request):
    return render(request, 'usEstudiante/notificaciones.html')

@role_required('Estudiante')
def progresoEstudiante(request):
    return render(request, 'usEstudiante/progreso.html')


#PROBANDO CONTINUAR VIENDO
def obtener_ultimo_item_pendiente(usuario, curso):
    # Buscar primer contenido no completado
    contenidos = Contenido.objects.filter(curso=curso).order_by('orden')
    for c in contenidos:
        if not ProgresoUsuario.objects.filter(usuario=usuario, contenido=c, completado=True).exists():
            return c

    # Buscar primera lección no completada
    lecciones = Leccion.objects.filter(modulo__curso=curso).order_by('modulo__orden', 'orden')
    for l in lecciones:
        if not ProgresoUsuario.objects.filter(usuario=usuario, leccion=l, completado=True).exists():
            return l

    return None  # Todo completado


def cursos_en_progreso(request):
    inscripciones = Inscripcion.objects.filter(usuario=request.user, estado='en_progreso')
    cursos_con_punto = []

    for inscripcion in inscripciones:
        contenido_pendiente = obtener_ultimo_item_pendiente(request.user, inscripcion.curso)
        cursos_con_punto.append({
            'curso': inscripcion.curso,
            'progreso': inscripcion.progreso,
            'contenido': contenido_pendiente
        })

    return render(request, 'usEstudiante/continuar_viendo.html', {'cursos_con_punto': cursos_con_punto})


@role_required('Estudiante')
def rutasEstudiante(request):
    return render(request, 'usEstudiante/rutas.html')

@role_required('Estudiante')
def cursosEstudiante(request):
    return render(request, 'usEstudiante/cursos.html')

@role_required('Estudiante')
def detalleCursoEstudiante(request):
    return render(request, 'usEstudiante/detalleCurso.html')

@role_required('Estudiante')
def tableroEstudiante(request):
    return render(request, 'usEstudiante/tablero.html')

@role_required('Estudiante')
def crearRutaEstudiante(request):
    return render(request, 'usEstudiante/crearRuta.html')

@role_required('Estudiante')
def verPerfilEstudiante(request):
    return render(request, 'usEstudiante/verPerfil.html')

@role_required('Estudiante')
def editarPerfilEstudiante(request):
    return render(request, 'usEstudiante/editarPerfilEstu.html')

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
            if request.user.is_authenticated:
                contexto = f"""
                Este es un usuario autenticado dentro de la plataforma educativa Rey Maestro.
                Puede hacer preguntas relacionadas con su progreso, cursos activos, o cómo avanzar en su nivel.
                Recuerda que ofrecemos acceso a cursos pregrabados, seguimiento personalizado, y soporte en vivo.
                También puedes recordarle al estudiante consultar su sección de 'mis cursos', contactar a su profesor, o acceder al foro estudiantil. 
                Nombre del usuario: {request.user.username}
                Primer nombre del usuario logeado: {request.user.first_name}
                email : {request.user.email}
                Solo en tu primer mensaje puedes empezar salundado tomado su Primer nombre del usuario logeado para que se sienta más comodo el usuario. 
                Recuerdale que puede si quiere hablar con un asesor real puede dar clic debajo del chat al botón de WhatsApp o escribir directamente al número +593968561304.
                """
            else:
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

