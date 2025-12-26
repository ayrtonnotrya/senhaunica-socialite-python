from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpRequest

def home(request: HttpRequest):
    return render(request, 'home.html')

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('/')
