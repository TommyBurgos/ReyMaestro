from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('usAdmin/', views.inicioAdmin, name="dashboard-adm"),
    path('usAdmin/detalleAlumnos', views.detalleUsuarios, name="detalleUsuarios-adm"),
    path('usuarios/<int:id>/ver-o-editar/', views.ver_o_editar_usuario, name='ver_o_editar'),
    path('usAdmin/<int:id>/resetearContra', views.resetContra_usuario, name="resetear_contrasena"),

    path('usAdmin/detalleCursos', views.detalleCursos, name="detalleCursos-adm"),
    path('usAdmin/detallePagos', views.detallePagos, name="detallePagos-adm"),
    path('usAdmin/detalleReportes', views.detalleReportes, name="reportes-adm"),
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




    #Estudiantes
    path('usEstudiante/chat', views.chatEstudiante, name="student_chat"),
    path('usEstudiante/notificaciones', views.notificacionesEstudiante, name="student_notificaciones"),
    path('usEstudiante/progreso', views.progresoEstudiante, name="student_progreso"),
    path('usEstudiante/rutas', views.rutasEstudiante, name="student_rutas"),
    path('usEstudiante/cursos', views.cursosEstudiante, name="student_cursos"),
    path('usEstudiante/detalleCurso', views.detalleCursoEstudiante, name="student_detallecurso"),

]
