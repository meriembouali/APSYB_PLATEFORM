import django_filters
from .models import Utilisateur
from django_filters import CharFilter



class user_filter(django_filters.FilterSet):
    email = CharFilter(field_name='email',lookup_expr='icontains' , label="E-mail")
    nom = CharFilter(field_name='nom',lookup_expr='icontains',label="Nom")
    prenom = CharFilter(field_name='prenom',lookup_expr='icontains',label="Prénom")
    age = CharFilter(field_name='age',lookup_expr='icontains',label="Age")
    class Meta:
        model = Utilisateur
        fields = ['email','nom','prenom','age']


