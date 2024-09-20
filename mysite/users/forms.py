# forms.py
from django import forms
from .models import Utilisateur

class register_form(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label="Password",
        required=False  
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label="Confirm Password",
        required=False  
    )

    class Meta:
        model = Utilisateur
        fields = ['email', 'nom', 'prenom', 'age', 'telephone', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password or password_confirmation:  
            if password != password_confirmation:
                self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)
        
        if commit:
            user.save()

        return user
