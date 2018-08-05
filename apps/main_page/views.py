from django.shortcuts import render


def constitution(request):
    return render(request, 'constitution.html')

def events(request):
    return render(request, 'events.html', {"events": []})

def index(request):
    return render(request, 'index.html')

def showcase(request):
    return render(request, 'showcase.html')

def industry(request):
    return render(request, 'industry.html')

def resources(request):
    return render(request, 'resources.html')

def hackathon13(request):
    return render(request, 'hackathonfa13.html')

def hackathon14(request):
    return render(request, 'hackathonfa14.html')

def hackathonsp15(request):
    return render(request, 'hackathonsp15.html')

def hackathonfa15(request):
    return render(request, 'index.html')

def hackathonsp16(request):
    return render(request, 'hackathonsp16.html')

def hackathonfa16(request):
    return render(request, 'hackathonfa16.html')
