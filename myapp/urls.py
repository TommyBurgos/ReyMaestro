from django.urls import path
from . import views
urlpatterns = [
    path('', views.inicio),
    path('usAdmin/', views.inicioAdmin),
    path('registro/', views.registroUser),
    path('usEstudiante/', views.inicioEstudiante)
]
