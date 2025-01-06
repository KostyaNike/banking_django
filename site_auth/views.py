from django.shortcuts import render

def auth(request):
    return render(request, 'site_auth/site_auth.html')

def login(request):
    return render(request, 'site_auth/login.html')

def reg(request):
    return render(request, 'site_auth/reg.html')