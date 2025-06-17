from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('usAdmin/', views.inicioAdmin, name="dashboard-adm"),
    path('usAdmin/detalleAlumnos', views.detalleUsuarios, name="detalleUsuarios-adm"),
    path('usuarios/<int:id>/ver-o-editar/', views.ver_o_editar_usuario, name='ver_o_editar'),
    path('usAdmin/<int:id>/resetearContra', views.resetContra_usuario, name="resetear_contrasena"),

    path('usAdmin/detalleCursos', views.detalleCursos, name="detalleCursos-adm"),
    path('cursos/listado/', views.listado_cursos, name='listado_cursos'),
    path('usAdmin/detalleCursos/crearCurso', views.crear_curso, name="crearCurso-adm"),    
    path('detalleCurso/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('leccion/<int:leccion_id>/ver/', views.ver_leccion, name='ver_leccion'),#Para vista ADMIN
    path('curso/<int:curso_id>/eliminar/', views.eliminar_curso, name='eliminar_curso'),
    path('curso/<int:curso_id>/contenido/nuevo/', views.agregar_contenido, name='agregar_contenido'),
    path('curso/<int:curso_id>/modulo/nuevo/', views.crear_modulo, name='crear_modulo'),
    path('modulo/<int:modulo_id>/leccion/nueva/', views.crear_leccion, name='crear_leccion'),


    path('usAdmin/detallePagos', views.detallePagos, name="detallePagos-adm"),

    path('usAdmin/detalleReportes', views.detalleReportes, name="reportes-adm"),
    path('generar-reporte/', views.generar_reporte, name='generar_reporte'),

    path('usAdmin/config', views.configuracionAdmin, name="configuracion-adm"),
    path('usAdmin/soporte', views.soporteAdmin, name="soporte-adm"),
    path('usAdmin/editarPerfil', views.editarPerfil, name="editarPerfil-adm"),
    path('editar-perfil/cambiar-password/', views.cambiar_password, name='cambiar_password'),

    path('registro/', views.registroUser),
    path('usEstudiante/', views.inicioEstudiante, name="student_dashboard"),
    path('usDenegado/', views.accesoDenegado, name="accesoDenegado"),   
    path('registroExitoso/',views.registroExitoso),
    path('usDocente/', views.inicioDocente, name="teacher_dashboard"),
    path('inicio/',views.custom_login),
    path("api/chatbot/", views.chatbot_response, name="chatbot_response"),
    path("logout/", views.signout, name="logout"),
    path('usAdmin/tablero/', views.ajedrez_vs_ia, name='tablero_vs_ia'),
    path('ajedrez/crear-partida/', views.crear_partida_ia, name='crear_partida_ia'),
    path('ajedrez/enviar-movimiento/', views.enviar_movimiento, name='enviar_movimiento'),
    path('ajedrez/estado-partida/<str:game_id>/', views.obtener_estado_partida, name='estado_partida'),

    path('mensajes/', views.bandeja_entrada, name='bandeja_entrada'),
    path('mensajes/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/enviados/', views.mensajes_enviados, name='mensajes_enviados'),
    path('mensajes/<int:mensaje_id>/', views.detalle_mensaje, name='detalle_mensaje'),



    #Estudiantes
    path('detalleCurso/Estudiante/<int:curso_id>/', views.detalle_curso_Estudiante, name='detalle_curso_Estudiante'),
    path('leccion/Estudiante/<int:leccion_id>/ver/', views.ver_leccion_Estudiante, name='ver_leccion_Estudiante'),#Para vista Estudiante
    path('usEstudiante/cursoProceso', views.cursos_en_progreso, name="cursoProceso"),
    path('usEstudiante/chat', views.chatEstudiante, name="student_chat"),
    path('usEstudiante/notificaciones', views.notificacionesEstudiante, name="student_notificaciones"),
    path('usEstudiante/progreso', views.progresoEstudiante, name="student_progreso"),
    path('usEstudiante/rutas', views.rutasEstudiante, name="student_rutas"),
    path('usEstudiante/cursos', views.cursosEstudiante, name="student_cursos"),
    path('usEstudiante/detalleCurso', views.detalleCursoEstudiante, name="student_detallecurso"),
    path('usEstudiante/tablero', views.tableroEstudiante, name="student_tablero"),
    path('usEstudiante/crearRuta', views.crearRutaEstudiante, name="student_crearRuta"),
    path('usEstudiante/verPerfil', views.verPerfilEstudiante, name="student_verPerfil"),
    path('usEstudiante/editarPerfilEstu', views.editarPerfilEstudiante, name="student_editarPerfil"),

]
