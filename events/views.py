from django.shortcuts import render
from auth_app.middlewares import auth

@auth
def list_events(request):
    return render(request, 'events/index.html')
