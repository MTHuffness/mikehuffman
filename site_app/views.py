from django.shortcuts import render


def homepage(request):
    return render(request, 'home.html')


def research_page(request):
    return render(request, 'research.html')
