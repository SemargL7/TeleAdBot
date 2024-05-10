from django.urls import path
import views

urlpatterns = [
    path('register-user/', views.register_user, name='register-user'),
    path('register-chat/', views.register_chat, name='register-chat')
]
