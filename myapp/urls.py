from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio),
    path('usAdmin/', views.inicioAdmin),
    path('registro/', views.registroUser),
    path('usEstudiante/', views.inicioEstudiante),    
    path("api/chatbot/", views.chatbot_response, name="chatbot_response"),

]
