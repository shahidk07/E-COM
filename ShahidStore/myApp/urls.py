from django.shortcuts import render
from django.urls import path,include
from . import views

print("""
========================================
🚀 ShahidStore Routes
========================================

🏠 Home
http://127.0.0.1:8000/

🛍️ Catalog
http://127.0.0.1:8000/catalog/

🛒 Cart
http://127.0.0.1:8000/cart/

📦 Orders
http://127.0.0.1:8000/orders/

========================================
""")

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
]