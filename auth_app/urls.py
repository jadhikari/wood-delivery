from django.urls import path
from .views import login_user, logout_user
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('accounts/', include('django.contrib.auth.urls')),
   
]