from django.shortcuts import render
from .models import Product
# Create your views here.

def home(request):
    return render(request, 'home_page.html')

def catalog(request):
    products=Product.objects.all()
    return render(request, 'products.html',{"products":products})