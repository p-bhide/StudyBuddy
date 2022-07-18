from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginpage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutpage, name='logout'),
    path('', views.home, name = 'home'),
    path('user/<slug:pk>', views.userProfile, name = 'user'),
    path('room/<slug:pk>', views.room, name = 'room'),
    path('create-room/', views.createRoom, name = 'create-room'),
    path('update-room/<str:pk>/', views.updateRoom,name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom,name='delete-room'),
    path('delete-message/<str:pk>/', views.deleteMessage,name='delete-message'),
    path('update-user/', views.updateUser,name='update-user'),
]