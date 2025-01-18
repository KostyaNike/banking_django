from site_auth.models import BankCard
from django.shortcuts import render

def home(request):
    return render(request, "home/home.html")