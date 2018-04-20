from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # localhost:8000/
    path('', views.index, name='index'),

    # localhost:8000/register/
    path('register/', views.register, name='register'),

    # localhost:8000/login/
    path('login/', views.login_user, name='login_user'),

    # localhost:8000/logout/
    path('logout/', views.logout_user, name='logout_user'),
]
