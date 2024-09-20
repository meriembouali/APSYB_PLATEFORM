from django.urls import path
from . import views
from dashboard import views as v1 
from users import views as v2

urlpatterns = [
    path('', views.first_page, name="first_page"),
    path("events/" , views.events , name="events"),
    path("events/<int:id>" , views.event_details , name="event_details"),
    path("events/delete_event/<int:id>" , views.delete_event , name="delete_event"),
    path("create_event/" , views.create , name="create_event"),
    path("update_event/<int:id>" , views.update , name="update_event"),
    path("register_event/<int:id>" , views.register_event , name="register_event"),
    path("my_registered_events/" , views.my_registered_events , name="my_registered_events"),
    path("unregister_event_confirmation/<int:id>" , views.unregister_event_confirmation , name="unregister_event_confirmation"),
    path("unregister_event/<int:id>" , views.unregister_event , name="unregister_event"),
    path('liste_des_inscrits/<int:id>' , views.liste_des_inscrits, name="liste_des_inscrits"),
    path('liste_des_inscrits_confirme/<int:id>' , views.liste_des_inscrits_confirme, name="liste_des_inscrits_confirme"),
    path('liste_des_inscrits_non_confirme/<int:id>' , views.liste_des_inscrits_non_confirme, name="liste_des_inscrits_non_confirme"),
    path('inscription_detail/<int:id>/', views.inscription_detail, name='inscription_detail'),
    path('toggle_participation/<int:id>/', views.toggle_participation, name='toggle_participation'),
    path('confirmer_inscription/<int:id>/', views.register_event_confirmed, name='confirmer_inscription'),
    path('recherche/', views.event_search, name='event_search'),
    path('add-live-link/<int:id>', views.add_live_stream_link, name='add_live_stream_link'),
]