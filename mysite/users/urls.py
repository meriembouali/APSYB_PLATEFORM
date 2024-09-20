from django.urls import path
from . import views 

urlpatterns = [
    path("home/" , views.home , name="home"),
    path("register/" , views.register , name="register"),
    path("login/" , views.login_user , name="login"),
    path('logout/' , views.logout_user, name="logout"),
    path('user_page/' , views.user_page, name="user_page"),
    path('users/' , views.users, name="users"),
    path('users/delete_user/<int:id>' , views.delete_user, name="delete_user"),
    path('create_user/' , views.create_user, name="create_user"),
    path('update_user/<int:id>' , views.update_user, name="update_user"),
    path('profile/' , views.user_profile, name="user_profile"),
    path('update_profile/' , views.update_user_profile, name="update_user_profile"),

]