from django.http import HttpResponse
from django.shortcuts import redirect, render
from requests import request
from .models import Product
from django.core.mail import send_mail
from django.core.paginator import Paginator
import psycopg2
import random

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
    
def connect():
    conn=psycopg2.connect(
                                database="shahidstore",
                                user="shahid",
                                password="12345678",
                                host="localhost",
                                port="5432",)
    return conn


def signin(request):
    if(request.method=="POST"):
        email=request.POST.get("email")
        password=request.POST.get("password")
        
        conn=connect()
        curr=conn.cursor()
        curr.execute("SELECT user_id,password from storeusers where email =%s ",(email,))
        user=curr.fetchone()
        if(user):
            user_id=user[0]
            actual_pass=user[1]
            typed_pass=password
            if(actual_pass==typed_pass):
                request.session["user_id"]=user_id
                request.session["is_authenticated"]=True
                return redirect("/")
            else:
                return render(request,"loginpage.html",{"message":"Incorrect password"})
        else:
            return render(request,"loginpage.html",{"message":"No user is registered with this email id"})
    return render(request,'loginpage.html')

def signup(request):
    if(request.method=="POST"):
        email=request.POST.get("email")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")

        
        otp=random.randint(100000,999999)
        send_mail("Shahid Store OTP Verification",
              f"Your OTP is {otp}", "viperoflegendkiller@gmail.com",
        [email],
        fail_silently=False,)

        request.session["otp"]=str(otp)
        request.session["email"]=email
        request.session["first_name"]=first_name
        request.session["last_name"]=last_name
        request.session["password"]=password

        return redirect('/verify/')
    
    return render(request,'signup.html')

def verify(request):
    if(request.method=="POST"):
        otp=request.session["otp"]
        entered_otp=request.POST.get("otp")
        if(otp==entered_otp):
            user_id=create_account(request)
            return redirect("/")
        else:
            return render(request,{"message":"failed"})
    else:
        return render(request,"verify.html")

def create_account(request):
    first_name=request.session["first_name"]
    last_name=request.session["last_name"]
    email=request.session["email"]
    password=request.session["password"]


    conn=connect()
    try:
        curr=conn.cursor()
        #create user and get user_id
        curr.execute("""INSERT INTO storeusers(first_name,last_name,email,password)
          VALUES(%s,%s,%s,%s) RETURNING user_id;
        """,(first_name,last_name,email,password))
   
        user_id=curr.fetchone()[0]

        #create a new cart for new user
        curr.execute("""
                INSERT INTO store_cart(user_id)
                VALUES (%s);""", (user_id,))
            
        conn.commit()

        #remove temporary sessions
        for key in ("otp","email","first_name","last_name","password"):
            request.session.pop(key,None)

        #log the new user in    
        request.session["user_id"]=user_id
        request.session["is_authenticated"]=True

       

    except Exception:
        conn.rollback()
        raise

    finally:
        curr.close()
        conn.close()
    
    return user_id

    


    
def cart(request):
    return(request,"cart_page.html")

# def add_to_cart(request):
#     product_id=request.POST.get(product_id)
#     quantity=request.POST.get(quantity)

#     db.connect()

