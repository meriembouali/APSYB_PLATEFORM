from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_function):
    def wrapper_function(request,*args,**kwargs):
        if request.user.is_authenticated:
            if request.user.groups.all()[0].name == "admin":
                return redirect('home')
            if request.user.groups.all()[0].name == "beneficiaire":
                return redirect('user_page')
        else: 
            return view_function(request,*args,**kwargs)
    return wrapper_function


def allowed_users(allowed_roles=[]):
    def decorator(view_function):
        def wrapper_function(request, *args, **kwargs):
            group =  None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print(f"Group found: {group}")
            else:
                print("No group found for the user.")
            if group in allowed_roles:
                print(f"Group {group} is in allowed roles: {allowed_roles}")
                return view_function(request, *args, **kwargs)
            else:
                print(f"Group {group} is NOT in allowed roles: {allowed_roles}")
            return HttpResponse("You are not allowed to view this page!") 
            
        return wrapper_function
    return decorator

