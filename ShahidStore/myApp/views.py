from decimal import Decimal

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
    from psycopg2.extras import RealDictCursor

    user_id=request.session["user_id"]
    conn=connect()
    curr=conn.cursor(cursor_factory=RealDictCursor)
    curr.execute("""select cart_id from store_cart where user_id=%s""",(user_id,))
    cart_id=curr.fetchone()["cart_id"]

    curr.execute("""select ci.cart_item_id,ci.product_id,ci.quantity,p.name,p.price,p.image_url,p.stock,p.description 
        from store_cart_item as ci 
        join "myApp_product" as p 
        on ci.product_id=p.id
        where ci.cart_id=%s""",(cart_id,))
    
    items=curr.fetchall()

    subtotal=Decimal("0.00")
    for item in items:
        item["total_price"]=item["price"]*item["quantity"]
        subtotal+=item["total_price"]

    return  render(request,"cart_page.html",{"items":items,"subtotal":subtotal})



def add_to_cart(request):
    from django.http import JsonResponse
    import json
    is_authenticated=request.session.get("is_authenticated",False)
    if(is_authenticated):
        user_id=request.session["user_id"]
        
        data=json.loads(request.body)
        product_id=data["product_id"]
        quantity=data["quantity"]
        conn=connect()
        try:
            curr=conn.cursor()
            curr.execute("select cart_id from store_cart where user_id =%s",(user_id,))
            cart_id=curr.fetchone()[0]
            curr.execute(""" insert into store_cart_item(cart_id, product_id, quantity) values(%s,%s,%s) 
            on conflict (cart_id,product_id)
            do update set
             quantity =store_cart_item.quantity+ excluded.quantity

             returning quantity,(xmax=0) as inserted;
            """,(cart_id,product_id,quantity,))

            new_quantity,inserted=curr.fetchone()
            if inserted:
                message="Item added to cart"
            else:
                message=f"Item quantity in cart increased by {quantity}"

            #update product_stock
            curr.execute("""update "myApp_product"
            set stock=stock - %s where id=%s returning stock""",(quantity,product_id))

            new_stock=curr.fetchone()[0]
            conn.commit()
            curr.close()
            conn.close()
            return JsonResponse({"message":message,"stock":new_stock},status=200)
            
        except Exception:
            raise       
    else:
        return JsonResponse({"message":"Please signin again"},status=401)



def logout(request):
    request.session.flush()
    return redirect("/signin/")