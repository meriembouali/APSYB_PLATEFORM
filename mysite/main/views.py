import json
import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import Evenement
from .forms import event_form 
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from .filters import event_filter
from Inscription.models import Inscription
from dashboard.views import dashboard_inscription
from users.views import user_page
from django.core.mail import EmailMessage
from django.conf import settings
from Inscription.utils import generate_qr_code
import mimetypes
from django.utils import timezone
from attestation.models import Attestation
from django.db.models import Q
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



@login_required(login_url="login")
def index(request):
    return render(request, 'main/base.html', {})


@login_required(login_url="login")
def home(response):
    return render(response, "main/home.html" , {})

@login_required(login_url="login")
def events(response):
    today = date.today()

    events = Evenement.objects.filter(date__gte=today)
    events_past = Evenement.objects.filter(date__lt=today)
    is_admin = response.user.is_superuser

    event_data = []
    event_past_data = []
    
    for event in events:
        num_inscriptions = Inscription.objects.filter(evenement=event).count()
        
        remaining_places = event.nombre_places - num_inscriptions
                
        event_data.append({
            'event': event,
            'num_inscriptions': num_inscriptions,
            'remaining_places': remaining_places,
        })

    for event_past in events_past:
        number_inscriptions = Inscription.objects.filter(evenement=event_past).count()
        
        number_participations = Inscription.objects.filter(evenement=event_past,participated=True).count()
                
        event_past_data.append({
            'event_past': event_past,
            'number_inscriptions': number_inscriptions,
            'number_participations': number_participations,
        })


    return render(response, "main/events/events.html",{
        'event_data':event_data,
        'event_past_data': event_past_data,
        'is_admin':is_admin,
        })




@login_required(login_url="login")
def event_details(response,id):
    event = Evenement.objects.get(id=id)
    is_admin = response.user.is_superuser
    return render(response, "main/events/event_details.html",{
        'event':event,
        'is_admin':is_admin
        }) 

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def create(response): 
    if response.method == "POST":
        form = event_form(response.POST, response.FILES)
        if form.is_valid():
            event = form.save()
            return redirect("event_details", id=event.id)
    else:
        form = event_form()

    return render(response, "main/events/create_event.html", {"form": form})

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def update(response,id): 
    event = Evenement.objects.get(id=id) 
    form = event_form(instance=event)
    if response.method == "POST":
        form = event_form(response.POST,response.FILES,instance=event)
        if form.is_valid():
            form.save()
        return redirect("event_details", id = event.id) 

    return render(response, "main/events/update_event.html",
                  {"form":form,
                   "event_id":id}) 


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def delete_event(response,id): 
    event = Evenement.objects.get(id=id)
    event.delete()
    return redirect("events")


@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
def inscription_detail(request,id):
    inscription = Inscription.objects.get(id=id)
    return render(request, 'main/inscription_detail.html', {'inscription': inscription})

@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
@csrf_exempt
@require_POST
def register_event(response,id): 
    event = Evenement.objects.get(id=id)
    user = response.user
    if Inscription.objects.filter(Utilisateur=user,evenement=event).exists():
        return JsonResponse({"status": "error", "message": "Vous êtes déja inscrit à cet événement!"})
    
    if Inscription.objects.filter(
        Utilisateur=user,
        evenement__date=event.date,
        evenement__heure=event.heure
    ).exists():
        return JsonResponse({"status": "error", "message": "Vous ne pouvez pas vous inscrire à deux événements à la même date et heure !"})
    inscription = Inscription(Utilisateur=user,evenement=event,statut_paiement="non_paye")
    
    nb_inscriptions = Inscription.objects.filter(evenement=event).count()
    if nb_inscriptions >= event.nombre_places:
        envoyer_notification_admin(event)
        return JsonResponse({"status": "error", "message": "Le nombre maximum d'inscriptions pour cet événement est atteint !"})
    inscription.save()
    attestation = Attestation.objects.create(
        Inscription=inscription,
        date_emission=None, 
        cachet="Cachet par défaut",  
        signature="Signature par défaut",  
        etat='non_genere'
    )
    attestation.save()
    return JsonResponse({"status": "success", "message": "Inscription réussie!"})

 
def send_qr_code_invit_email(to_email, qr_code_file, event,invitation_image_file):
    subject = f"Inscription pour l'événement {event.nom}"
    body = f"Cher participant,\n\nVous êtes inscrit avec succès à {event.nom}. Veuillez trouver ci-joints votre QR code et votre invitation.\n\nCordialement,\nL'équipe de l'événement"

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )


    qr_code_file.seek(0)
    email.attach('qr_code.png', qr_code_file.read(), 'image/png')

    if invitation_image_file:
        invitation_image_file.seek(0)
        content_type, encoding = mimetypes.guess_type(invitation_image_file.name)
        if content_type is None:
            content_type = 'application/octet-stream'

        email.attach(invitation_image_file.name, invitation_image_file.read(), content_type)
    email.send()

def envoyer_notification_admin(event):
    subject = f"Capacité maximale atteinte pour {event.nom}"
    body = f"L'événement {event.nom} a atteint sa capacité maximale ({event.nombre_places} places). Les inscriptions sont désormais fermées."
    
    # Envoyer un email à l'administrateur
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["iman45665400@gmail.com"],
    )

    email.send()

@login_required(login_url="login")
def register_event_confirmed(response,id): 
    user = response.user
    event = Evenement.objects.get(id=id)
    inscription = Inscription.objects.get(Utilisateur=user,evenement=event)
    if inscription.confirmed : 
        return HttpResponse("The inscription is already confirmed")
    else:
        inscription.confirmed = True
        inscription.save()

        qr_code_content = f"{user.email}-{event.nom}-{inscription.statut_paiement}"
        qr_code_file = generate_qr_code(qr_code_content)

        invitation_image_file = event.invitation_image

        send_qr_code_invit_email(user.email, qr_code_file, event,invitation_image_file)
        return redirect('inscription_detail', id=inscription.id)

@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
def unregister_event(response,id):
    user = response.user 
    event = Evenement.objects.get(id=id)
    inscription = Inscription.objects.filter(Utilisateur=user,evenement=event)
    if inscription.exists():
        inscription.delete()
    return redirect('my_registered_events')

@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
def unregister_event_confirmation(response, id):
    event = Evenement.objects.get(id=id)
    return render(response, "main/events/unregister_event.html", {"event": event})

@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
def my_registered_events(request):
    user = request.user
    inscriptions = Inscription.objects.filter(Utilisateur=user,participated=False)
    events_with_status = [
        {
            'event': inscription.evenement,
            'inscription': inscription
        }
        for inscription in inscriptions
    ]
    
    return render(request, 'main/events/my_registered_events.html', {'events_with_status': events_with_status})

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def liste_des_inscrits(request, id):
    event = Evenement.objects.get(id=id)
    inscriptions = Inscription.objects.filter(evenement=event)
    num_inscriptions = inscriptions.count()
    
    utilisateurs_inscrits = [
        {'utilisateur': inscription.Utilisateur, 'inscription': inscription}
        for inscription in inscriptions
    ]
    
    return render(request, 'main/events/liste_des_inscrits.html', {
        'event': event,
        'utilisateurs_inscrits': utilisateurs_inscrits,
        'num_inscriptions': num_inscriptions,
        'is_confirmed_view': False,
    })

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def liste_des_inscrits_confirme(request, id):
    event = Evenement.objects.get(id=id)
    inscriptions = Inscription.objects.filter(evenement=event,confirmed=True)
    
    utilisateurs_inscrits = [
        {'utilisateur': inscription.Utilisateur, 'inscription': inscription}
        for inscription in inscriptions
    ]
    
    return render(request, 'main/events/liste_des_inscrits.html', {
        'event': event,
        'utilisateurs_inscrits': utilisateurs_inscrits,
        'is_confirmed_view': True
    })

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def liste_des_inscrits_non_confirme(request, id):
    event = Evenement.objects.get(id=id)
    inscriptions = Inscription.objects.filter(evenement=event,confirmed=False)
    
    utilisateurs_inscrits = [
        {'utilisateur': inscription.Utilisateur, 'inscription': inscription}
        for inscription in inscriptions
    ]
    
    return render(request, 'main/events/liste_des_inscrits.html', {
        'event': event,
        'utilisateurs_inscrits': utilisateurs_inscrits,
        'is_confirmed_view': False,
    })

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def toggle_participation(request,id):
    if request.method == "POST":
        inscription = Inscription.objects.get(id=id)

        current_time = timezone.now()
        if inscription.evenement.date > current_time.date():
            return JsonResponse({'success': False, 'message': "Vous ne pouvez pas confirmer la présence avant la date de l'événement."})


        data = json.loads(request.body)
        inscription.participated = data.get('participated', False)
        inscription.save()
        return JsonResponse({'success': True, 'message': 'Participation confirmée.'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url="login")
def event_search(request):
    today = date.today()
    query = request.GET.get('q')  
    events = Evenement.objects.filter(date__gte=today)
    event_data = []


    if query:
        events = events.filter(
            Q(nom__icontains=query) |  
            Q(lieu__icontains=query) |  
            Q(description__icontains=query) |  
            Q(date__icontains=query) |  
            Q(heure__icontains=query) |
            Q(details_lieu__icontains=query) |
            Q(public_vise__icontains=query) |
            Q(organisateurs__icontains=query) |
            Q(objectifs__icontains=query) 

        )

    
    for event in events:
        num_inscriptions = Inscription.objects.filter(evenement=event).count()
        
        remaining_places = event.nombre_places - num_inscriptions
                
        event_data.append({
            'event': event,
            'remaining_places': remaining_places,
        })

    return render(request, "main/events/events.html",{'event_data':event_data})




@login_required
def first_page(request):
    if request.user.is_superuser:
        return dashboard_inscription(request)
    else:
        return user_page(request)
    


def add_live_stream_link(request, id):
    if request.method == "POST":
        live_stream_link = request.POST.get('live')
        print("the event live link:", live_stream_link)
        event = get_object_or_404(Evenement, id=id)

        if live_stream_link:
            event.live = live_stream_link
        else:
            event.live = None
        
        event.save()
        return redirect('event_details', id=event.id)

    return HttpResponse(status=400)
