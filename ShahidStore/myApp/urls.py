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

📦 signup
http://127.0.0.1:8000/signup/

========================================
""")

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('details/<int:id>/', views.details, name='details'),
    #  path('signin', views.signin, name='signin'),
    path('verify/', views.verify, name='verify'),
    path("cart/", views.cart, name="cart"),
    path("cart/add/", views.add_to_cart, name="cart_add"),
    # path("cart/update/", views.update_cart, name="cart_update"),
    # path("cart/remove/", views.remove_from_cart, name="cart_remove"),
]