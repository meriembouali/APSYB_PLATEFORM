from django.urls import path
from . import views

urlpatterns = [
    path("Inscription/" , views.dashboard_inscription , name="dashboard_inscription"),
    path("Participation/" , views.dashboard_participation , name="dashboard_participation"),
    path('rapport-mensuel/', views.generer_rapport_mensuel, name='generer_rapport_mensuel'),
    path('rapport-annuel/', views.generer_rapport_annuel, name='generer_rapport_annuel'),
    
]