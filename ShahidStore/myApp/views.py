from django.shortcuts import render
from .models import Product
# Create your views here.

def home(request):
    return render(request, 'home_page.html')

def catalog(request):
    CATEGORY_MAP = {
    "Electronics": ["electronics_gaming","electronics_mobile","electronics_camera",],
    "Fashion": ["apparel","footwear","bags","fashion_accessories",],
    "Beauty": ["beauty_skincare", ],
    "Home": ["furniture_home","kitchen_dining",],
    "Sports": ["sports_outdoors",],
}
    
    products=Product.objects.all()
    return render(request, 'catalog.html',{"products":products,"categories":CATEGORY_MAP.keys()})