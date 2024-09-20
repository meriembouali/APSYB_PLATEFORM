from django.utils import timezone
from django.db import models
from users.models import Utilisateur
from main.models import Evenement 
from .utils import generate_qr_code

# Create your models here.

class Inscription(models.Model):
    STATUTPAIEMENT_CHOICES = [
        ('non_paye', "Non payé"),
        ('paye' , 'Payé'),
        ('especes_sur_place' , 'espèces sur place'),
    ]
    Utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    evenement = models.ForeignKey(Evenement,on_delete=models.CASCADE)
    statut_paiement = models.CharField(max_length=30, choices=STATUTPAIEMENT_CHOICES, default="Non payé")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    participated = models.BooleanField(default=False) # L'utilisateur a participé a l'evenement (ADMIN)
    confirmed = models.BooleanField(default=False) # L'utilisateur a confirmé son inscription (benef)




    class Meta: 
        unique_together = ('Utilisateur' , 'evenement')

    def __str__(self):
        return f"{self.Utilisateur.prenom} - {self.evenement.nom}"
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            qr_code_content = f"{self.Utilisateur.email}-{self.evenement.nom}-{self.statut_paiement}"
            qr_code_file = generate_qr_code(qr_code_content)
            self.qr_code.save('qr_code.png', qr_code_file, save=False)
        super().save(*args, **kwargs)




