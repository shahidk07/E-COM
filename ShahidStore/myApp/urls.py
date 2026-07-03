from django.shortcuts import render
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home')
]