from django.shortcuts import render,redirect
from .forms import register_form
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users,unauthenticated_user
from .models import Utilisateur, UserProfile
from .filters import user_filter
from Inscription.models import Inscription
from attestation.models import Attestation
from datetime import date
from main.models import Evenement





# Create your views here.


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def home(request):
    user = request.user.prenom  
    return render(request, 'users/home.html', {'user': user})



@login_required(login_url="login")
@allowed_users(allowed_roles=['beneficiaire'])
def user_page(request):
    user = request.user.prenom
    today = date.today()

    events = Evenement.objects.filter(date__gte=today).order_by('-date')[:8]
    
    event_data = []
    
    for event in events:
        num_inscriptions = Inscription.objects.filter(evenement=event).count()
        
        remaining_places = event.nombre_places - num_inscriptions
                
        event_data.append({
            'event': event,
            'remaining_places': remaining_places,
        })
    
    return render(request, 'users/user_page.html', {
        'user': user,
        'event_data': event_data,
    })
     
     
@unauthenticated_user
def register(request):
    if request.method == 'POST':
        form = register_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.set_password(form.cleaned_data['password'])
            user.save()
            group = Group.objects.get(name='beneficiaire')
            user.groups.add(group)
            user.save()
            messages.success(request, f"L'utilisateur {user.prenom} a été crée avec succès.")
            return redirect('login')
    else:
        form = register_form()
    return render(request,'users/register.html',{'form':form})


@unauthenticated_user
def login_user(request):
    if request.method == 'POST': 
        email = request.POST.get("email")
        password= request.POST.get("password")

        user= authenticate(request,email=email,password=password) 

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect('dashboard_inscription')
            else:
                return redirect('user_page')
        else:
                messages.error(request, "E-mail ou mot de passe invalide.")

    return render(request,"users/login.html",{})

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def users(request):
    users = Utilisateur.objects.filter(is_superuser = False)
    my_Filter = user_filter(request.GET,queryset=users)
    users = my_Filter.qs
    return render(request,'users/users.html' , 
            {'users':users,
             'my_Filter':my_Filter})


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def create_user(request):
    if request.method == 'POST':
        form = register_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            group = Group.objects.get(name='beneficiaire')
            user.groups.add(group)
            user.save()
            messages.success(request, f'The user {user.prenom} was created successfully.')
            return redirect('users')
    else:
        form = register_form
    return render(request,'users/create_user.html',{'form': form})
            

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def update_user(request,id):
    user = Utilisateur.objects.get(id=id)
    form = register_form(instance=user)
    if request.method == 'POST':
        form = register_form(request.POST,instance=user)
        print(f"Updating user: {form.instance.id}")
        if form.is_valid():
            print(f"Updating user: {form.instance.id}")
            form.save()
            print(f"Updated user: {form.instance.id}")
        return redirect('users')
    return render(request,'users/update_user.html',
            {'form': form,
             'user_id': id})


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def delete_user(request,id):
    user = Utilisateur.objects.get(id=id)
    user.delete()
    return redirect('users')

@login_required(login_url="login")
def user_profile(request):
    user = request.user
    events_with_attestations = []

    if not user.is_superuser:
        inscriptions = Inscription.objects.filter(Utilisateur=user, participated=True)

        for inscription in inscriptions:
            attestation = Attestation.objects.filter(Inscription=inscription).first()
            events_with_attestations.append({
                'event': inscription.evenement,
                'attestation': attestation,
            })

    return render(request, 'users/user_profile.html', {
        'user': user,
        'events_with_attestations': events_with_attestations,
    })


@login_required(login_url="login")
def update_user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = register_form(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  
    else:
        form = register_form(instance=user)  

    return render(request, 'users/update_user_profile.html', {'form': form})

