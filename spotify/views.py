from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, World!")


def index2(request):
    return render(request, "index.html")
# Create your views here.
