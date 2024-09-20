from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Attestation
from Inscription.models import Inscription
from PIL import Image, ImageDraw, ImageFont
import io,os
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def generate_attestation(request, inscription_id):
    inscription = get_object_or_404(Inscription, id=inscription_id)

    if not inscription.participated:
        return JsonResponse({
            'success': False,
            'message': "Erreur : Vous ne pouvez pas générer l'attestation car la présence n'a pas été confirmée."
        })

    attestation = get_object_or_404(Attestation, Inscription=inscription)

    template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'attestation.jpg')
    img = Image.open(template_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    draw = ImageDraw.Draw(img)

    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DancingScript-Variable.ttf')
    name = f"{inscription.Utilisateur.nom} {inscription.Utilisateur.prenom}"
    date = inscription.evenement.date.strftime('%d/%m/%Y')
    event_name = inscription.evenement.nom

    draw.text((2200, 2150), f"{name}", font=ImageFont.truetype(font_path, 450), fill="#03224c")
    draw.text((1260, 3750), f"{date}", font=ImageFont.truetype(font_path, 120), fill="#03224c")
    draw.text((2300, 2930), f"{event_name}", font=ImageFont.truetype(font_path, 150), fill="#03224c")

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    attestation.date_emission = timezone.now().date()
    if attestation.etat == 'non_genere':

        image_name = f"{inscription.Utilisateur.nom}_{inscription.Utilisateur.prenom}.jpg"
        attestation.image.save(image_name, ContentFile(buffer.getvalue()), save=False)

        subject = "Votre attestation de participation"
        message = f"Veuillez trouver ci-joint votre attestation de participation à l'événement {event_name} le {date}."
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [inscription.Utilisateur.email]

        email = EmailMessage(subject, message, email_from, recipient_list)
        email.attach(f'{inscription.Utilisateur.nom}.jpg', buffer.getvalue(), 'image/jpeg')
        email.send()

        attestation.etat = 'genere'

    attestation.save()

    filename = f"{inscription.Utilisateur.nom}_{inscription.Utilisateur.prenom}.jpg"
    response = HttpResponse(buffer, content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
