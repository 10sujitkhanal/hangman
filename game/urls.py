from django.urls import path
from . import views

urlpatterns = [
    path('', views.hangman_game, name='hangman_game'),
    path('reset/', views.reset_game, name='reset_game'),

    path('upload/', views.upload_csv, name='upload_csv'),
    path('upload/success/', views.upload_success, name='upload_success'),
]