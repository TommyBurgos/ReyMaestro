from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# Modelo de Tipos de Usuario
class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    imgPerfil = models.ImageField(default='imageDefault.png', upload_to='users/')
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE, null=True, blank=True)
    rol = models.ForeignKey('Rol', on_delete=models.CASCADE, null=True, blank=True)


# Modelo de Pagos
class Pago(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    estado_pago = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('completado', 'Completado'), ('fallido', 'Fallido')], default='pendiente')

# Modelo de Cursos
class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Profesor'})
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    destacado = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=20,
        choices=[('borrador', 'Borrador'), ('publicado', 'Publicado'), ('inactivo', 'Inactivo')],
        default='borrador'
    )
    nivel_dificultad = models.CharField(
        max_length=20,
        choices=[('basico', 'Básico'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado')],
        default='basico'
    )
    @property
    def primer_video(self):
        return self.contenido_set.filter(tipo_contenido='video').first()


    def __str__(self):
        return f"{self.titulo} ({self.get_nivel_dificultad_display()})"


class HistorialAcciones(models.Model):
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Administrador'})
    accion = models.CharField(max_length=255)
    fecha_accion = models.DateTimeField(auto_now_add=True)

# Modelo de Niveles
class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)  # Permite organizar los módulos en el curso

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"

class Leccion(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    tipo_contenido = models.CharField(
        max_length=10,
        choices=[('video', 'Video'), ('documento', 'Documento'), ('texto', 'Texto')]
    )
    descripcion = models.TextField(blank=True, null=True)
    url_contenido = models.URLField(blank=True, null=True)
    archivo = models.FileField(upload_to="lecciones/", blank=True, null=True)
    imagen = models.ImageField(upload_to="imagenes_lecciones/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=1)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    # 🔥 Nuevo campo de aprobación
    estado_aprobacion = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado')
        ],
        default='pendiente'
    )
    comentarios_admin = models.TextField(blank=True, null=True)  # Comentarios del admin en caso de rechazo

    def __str__(self):
        return f"{self.modulo.titulo} - {self.titulo}"

class RevisionContenido(models.Model):
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Administrador'})
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    fecha_revision = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(
        max_length=20,
        choices=[
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado')
        ]
    )
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Revisión por {self.administrador.username} - {self.decision}"


# Modelo de Contenidos
class Contenido(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    nivel = models.ForeignKey(Modulo, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    tipo_contenido = models.CharField(
        max_length=10, choices=[('video', 'Video'), ('documento', 'Documento'), ('texto', 'Texto')]
    )
    url_contenido = models.URLField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to="documentos/", blank=True, null=True)
    imagen = models.ImageField(upload_to="imagenes/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=1)  # Permite organizar el contenido
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
        
# Modelo de Inscripciones
class Inscripcion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('en_progreso', 'En Progreso'), ('completado', 'Completado')], default='en_progreso')
    progreso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Progreso en porcentaje
    ultima_actividad = models.DateTimeField(auto_now=True)  # Última vez que interactuó con el curso

    def __str__(self):
        return f'{self.usuario.username} - {self.curso.titulo}'



# Modelo de Progreso de Usuarios
class ProgresoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

# Modelo de Calificaciones
class Calificacion(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_calificacion = models.DateTimeField(auto_now_add=True)


class RegistroConexion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_conexion = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Opcional para registrar IP

def actualizar_progreso(inscripcion):
    total_contenidos = Contenido.objects.filter(curso=inscripcion.curso).count()
    completados = ProgresoUsuario.objects.filter(usuario=inscripcion.usuario, completado=True).count()
    progreso = (completados / total_contenidos) * 100
    inscripcion.progreso = progreso
    inscripcion.save()


class Foro(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class ComentarioForo(models.Model):
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

class ParticipacionForo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    cantidad_comentarios = models.PositiveIntegerField(default=0)

def actualizar_participacion(usuario, foro):
    participacion, creado = ParticipacionForo.objects.get_or_create(usuario=usuario, foro=foro)
    participacion.cantidad_comentarios += 1
    participacion.save()


# Registro de actividades del profesor
class ActividadProfesor(models.Model):
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Profesor'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_actividad = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Actividad de {self.profesor.username} en {self.curso.titulo}"


# Personalización del panel de administración para asignar profesores
from django.contrib import admin

class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'profesor', 'estado', 'nivel_dificultad')
    list_filter = ('estado', 'nivel_dificultad')
    search_fields = ('titulo', 'profesor__username')
    autocomplete_fields = ['profesor']


# Evaluaciones y encuestas de satisfacción
class Examen(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class PreguntaExamen(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    texto_pregunta = models.TextField()
    opcion_a = models.CharField(max_length=255)
    opcion_b = models.CharField(max_length=255)
    opcion_c = models.CharField(max_length=255)
    opcion_d = models.CharField(max_length=255)
    respuesta_correcta = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

class EncuestaSatisfaccion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    pregunta = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class RespuestaEncuesta(models.Model):
    encuesta = models.ForeignKey(EncuestaSatisfaccion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)


from django.contrib.auth import get_user_model

Usuario = get_user_model()

class Mensaje(models.Model):
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    asunto = models.CharField(max_length=255)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.asunto} de {self.remitente} para {self.destinatario}"