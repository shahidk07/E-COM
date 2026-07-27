from django.shortcuts import render
from requests import request
from .models import Product
from django.core.mail import send_mail
from django.core.paginator import Paginator
import psycopg2
# Create your views here.

def home(request):
    new_products=Product.objects.order_by("-created_at")[:6]
    categories = [
        "Electronics",
        "Fashion",
        "Beauty",
        "Home",
        "Sports"
    ]
    
    return render(
        request,
        "namuna.html",
        {
            "new_products": new_products,
            "categories": categories
        }
    )

def catalog(request):
    CATEGORY_MAP = {
    "Electronics": ["electronics_gaming","electronics_mobile","electronics_camera",],
    "Fashion": ["apparel","footwear","bags","fashion_accessories",],
    "Beauty": ["beauty_skincare", ],
    "Home": ["furniture_home","kitchen_dining",],
    "Sports": ["sports_outdoors",],
}   
    products = Product.objects.all()
    search=request.GET.get("search")
    selected=request.GET.get("category")
    sort = request.GET.get("sort")
    
    if search:
        products=products.filter(
            name__icontains=search)

    if selected and selected in CATEGORY_MAP:
        products=products.filter(
            category__in=CATEGORY_MAP[selected]
        )
    
    if sort=="name":
        products=products.order_by("name")
    
    elif sort =="priceLow":
        products=products.order_by("price")
    
    elif sort== "priceHigh":
        products=products.order_by("-price")
        
    paginator=Paginator(products,20)
    page_number=page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog.html',
                  {"products":page_obj,
                   "page_obj":page_obj,
                   "categories":CATEGORY_MAP.keys(),
                    "selected_category":selected})


def details(request,id):
    product=Product.objects.get(id=id)
    return render(request,'prod_details.html',{"product":product})

# def cart(request):
    


# def signin(request):
#     return render(request,'loginpage.html')


def signup(request):
    if(request.method=="POST"):
        email=request.POST.get("email")
        import random
        otp=random.randint(100000,999999)
        send_mail("Shahid Store OTP Verification",
              f"Your OTP is {otp}", "viperoflegendkiller@gmail.com",
        [email],
        fail_silently=False,)

        request.session["otp"]=str(otp)
        request.session["signup_email"]=email

        conn=psycopg2.connect(
            database="shahidstore",
            user="shahid",
            password="12345678",
            host="localhost",
            port="5432",)
        return render(request,"verify.html")
    
    return render(request,'signup.html')

def verify(request):
    if(request.method=="POST"):
        otp=request.session["otp"]
        entered_otp=request.POST.get("otp")
        if(otp==entered_otp):
            return(request,{"message":"success"})
        else:
            return(request,{"message":"failed"})
    else:
        return(request,"verify.html")

def cart(request):
    return(request,"cart_page.html")

def add_to_cart(request):
    product_id=request.POST.get(product_id)
    quantity=request.POST.get(quantity)

    db.connect()