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
    path('registro/', views.registroUser),
    path('usEstudiante/', views.inicioEstudiante, name="student_dashboard"),
    path('usDenegado/', views.accesoDenegado, name="accesoDenegado"),   
    path('registroExitoso/',views.registroExitoso),
    path('usDocente/', views.inicioDocente, name="teacher_dashboard"),
    path('inicio/',views.custom_login),
    path("api/chatbot/", views.chatbot_response, name="chatbot_response"),
    path("logout/", views.signout, name="logout"),
    #Estudiantes
    path('usEstudiante/chat', views.chatEstudiante, name="student_chat"),
    path('usEstudiante/notificaciones', views.notificacionesEstudiante, name="student_notificaciones"),
    path('usEstudiante/progreso', views.progresoEstudiante, name="student_progreso"),
    path('usEstudiante/rutas', views.rutasEstudiante, name="student_rutas"),

]
