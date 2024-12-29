from django.shortcuts import render, redirect

def home(request):
    if not request.user.is_authenticated:
        return redirect("auth_sys:login")
    return render(request, "home.html")