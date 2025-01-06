from django.shortcuts import render

def home(request):
    return render(
        request,
        'home/home.html',
        {
            'is_authenticated': False,
        }
    )