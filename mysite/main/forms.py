from django import forms
from .models import Evenement

class event_form(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = [
            'nom', 'description', 'lieu', 'details_lieu', 'public_vise',
            'nombre_places', 'organisateurs', 'objectifs','programme', 'date', 'heure', 'diffusion_directe','invitation_image','event_image',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'max_length': 255}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'lieu': forms.TextInput(attrs={'max_length': 255}),
            'details_lieu': forms.Textarea(attrs={'rows': 4}),
            'public_vise': forms.Textarea(attrs={'rows': 4}),
            'nombre_places': forms.NumberInput(),
            'organisateurs': forms.TextInput(attrs={'max_length': 255}),
            'objectifs': forms.Textarea(attrs={'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure': forms.TimeInput(attrs={'type': 'time'}),
            'diffusion_directe': forms.CheckboxInput(),
        }
