from django.db import models

# Create your models here.
class Evenement(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    lieu = models.CharField(max_length=255)
    details_lieu = models.TextField()
    public_vise = models.TextField()
    nombre_places = models.IntegerField() 
    organisateurs = models.CharField(max_length=255)
    objectifs = models.TextField()
    programme = models.TextField(blank=True, null=True)
    date = models.DateField()
    heure = models.TimeField()
    diffusion_directe = models.BooleanField(default = True)
    invitation_image = models.ImageField(upload_to='event_invitations/', blank=True, null=True)
    event_image = models.ImageField(upload_to='event_images/' , blank=True, null=True)
    live = models.URLField(max_length=500, blank=True, null=True) 


    def __str__(self):
        return self.nom

