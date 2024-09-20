from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# Create your models here.

class UtilisateurManager(BaseUserManager):
    def create_superuser(self, email, nom, prenom, age, telephone, password=None, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)




        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')
        return self.create_user(email, nom, prenom, age, telephone, password, **other_fields)
    


    def create_user(self, email, nom, prenom, age, telephone, password=None, **other_fields):
        if not email:
            raise ValueError(('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom,prenom=prenom,age=age,telephone=telephone,**other_fields)
        user.set_password(password)
        user.save()
        return user

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('beneficiaire', 'Bénéficiaire'),
    ]
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    age = models.IntegerField()
    telephone = models.CharField(max_length=20)
    password = models.CharField(max_length=200)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects=UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'age', 'telephone']

    def __str__(self):
        return self.email
    


class UserProfile(models.Model):
    user = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.email