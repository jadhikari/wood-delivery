from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login , logout
from .middlewares import auth, guest

@guest
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('welcome')
    else:
        initial_data = {'username': '', 'password': ''}
        form = AuthenticationForm(initial = initial_data)
    
    return render(request, 'auth_app/login.html', {'form':form})
            


def logout_user(request):
    logout(request)
    return redirect('login_user')
