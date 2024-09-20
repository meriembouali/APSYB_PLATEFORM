import django_filters
from .models import Evenement
from django_filters import CharFilter


class event_filter(django_filters.FilterSet):
    nom = CharFilter(field_name='nom',lookup_expr='icontains' , label="Nom de l'evenement")
    lieu = CharFilter(field_name='lieu',lookup_expr='icontains',label="Lieu de l'evenement")
    date = CharFilter(field_name='date',lookup_expr='icontains',label="Date de l'evenement")
    heure = CharFilter(field_name='heure',lookup_expr='icontains',label="Heure de l'evenement")
    class Meta:
        model = Evenement
        fields = ['nom','lieu','date','heure']
