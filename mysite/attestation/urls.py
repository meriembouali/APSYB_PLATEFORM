from django.urls import path
from . import views

urlpatterns = [
    path('generate_attestation/<int:inscription_id>/', views.generate_attestation, name='generate_attestation'),
]