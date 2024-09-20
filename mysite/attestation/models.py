from django.db import models
from Inscription.models import Inscription

# Create your models here.

class Attestation(models.Model):
    ETAT_CHOICES = [
        ('non_genere', "Non généré"),
        ('genere' , 'Généré'),
    ]
    Inscription = models.OneToOneField(Inscription,on_delete=models.CASCADE)
    date_emission = models.DateField(null=True, blank=True)
    cachet = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    etat = models.CharField(max_length=30, choices=ETAT_CHOICES, default='Non généré')
    image = models.ImageField(upload_to='attestations/', null=True, blank=True)

    def __str__(self):
        return f"Attestation - {self.Inscription.Utilisateur.prenom} - {self.Inscription.evenement.nom}"
    
