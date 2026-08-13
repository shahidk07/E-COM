import json
import psycopg2
import random
from decimal import Decimal
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Product


# Create your views here.

def home(request):
    new_products=Product.objects.order_by("-created_at")[:6]
    categories = [
        {"name": "Electronics", "image": "images/electronics.jpg"},
        {"name": "Fashion", "image": "images/accessories.webp"},
        {"name": "Beauty", "image": "images/bgt.jpg"},
        {"name": "Home", "image": "images/decoration.jpg"},
        {"name": "Sports", "image": "images/fitness1.jpeg"}
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
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog.html',
                  {"products":page_obj,
                   "page_obj":page_obj,
                   "categories":CATEGORY_MAP.keys(),
                    "selected_category":selected})


def details(request,id):
    product=Product.objects.get(id=id)
    return render(request,'prod_details.html',{"product":product})

    
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

        conn=connect()
        curr=conn.cursor()
        curr.execute(""" select email from storeusers where email=%s""",(email,))
        store_email=curr.fetchone()
        conn.close()
        curr.close()
        if(not store_email):
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
        else:
            return JsonResponse( {"message": "Email already registered."}, status=409
)  
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
        try:
            curr.execute("""INSERT INTO storeusers(first_name,last_name,email,password)
              VALUES(%s,%s,%s,%s) RETURNING user_id;
            """,(first_name,last_name,email,password))
            
        except Exception as e:
            conn.rollback()
            return render(request,"signup.html",{
                "message":str(e)
            })
          
            
        user_id=curr.fetchone()[0]

        #create a new cart for new user
        curr.execute("select coupon_id from store_coupon where code=%s and is_active=True"
                     ,("FREE100",))
        coupon_row = curr.fetchone()

        if coupon_row is None:
            raise Exception("FREE100 coupon does not exist or is inactive")

        coupon_id = coupon_row[0]
        
        curr.execute("""
                INSERT INTO store_cart(user_id,applied_coupon_id)
                VALUES (%s,%s);""", (user_id,coupon_id))
            
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

    

def get_cart_summary(cart_id, curr):

    # Get cart items
    curr.execute("""
        SELECT
            ci.cart_item_id,
            ci.product_id,
            ci.quantity,
            p.name,
            p.price,
            p.image_url,
            p.stock,
            p.description
        FROM store_cart_item AS ci
        JOIN "myApp_product" AS p
            ON ci.product_id = p.id
        WHERE ci.cart_id = %s
    """, (cart_id,))

    items = curr.fetchall()

    # Calculate subtotal
    subtotal = Decimal("0.00")

    for item in items:
        item["total_price"] = item["price"] * item["quantity"]
        subtotal += item["total_price"]

    # Get currently applied coupon data
    curr.execute("""
        SELECT
            c.applied_coupon_id,
            cp.code,
            cp.discount_type,
            cp.discount_value,
            cp.minimum_order,
            cp.maximum_discount
        FROM store_cart AS c
        LEFT JOIN store_coupon AS cp
            ON c.applied_coupon_id = cp.coupon_id
        WHERE c.cart_id = %s
    """, (cart_id,))

    coupon_data = curr.fetchone()

    coupon_code = None
    discount = Decimal("0.00")
    
    if coupon_data["applied_coupon_id"] is not None:

        coupon_code = coupon_data["code"]

        # Check minimum order
        if subtotal >= coupon_data["minimum_order"]:

            if coupon_data["discount_type"] == "percentage":

                discount = (
                    subtotal *
                    coupon_data["discount_value"] /
                    Decimal("100")
                )

                # Apply maximum discount
                if coupon_data["maximum_discount"] is not None:
                    discount = min(
                        discount,
                        coupon_data["maximum_discount"]
                    )

            elif coupon_data["discount_type"] == "fixed":

                discount = min(
                    coupon_data["discount_value"],
                    subtotal
                )

            elif coupon_data["discount_type"] == "final_price":

                discount = max(
                    subtotal - coupon_data["discount_value"],
                    Decimal("0.00")
                )

    total = subtotal - discount
    return {
        "items": items,
        "coupon": coupon_code,
        "subtotal": subtotal,
        "discount": discount,
        "total": total
    }
    
def cart(request):
    from psycopg2.extras import RealDictCursor

    user_id=request.session["user_id"]
    if not user_id:
            return JsonResponse(
                {"success": False, "message": "Please login first"},
                status=401)
            
    conn=connect()
    curr=conn.cursor(cursor_factory=RealDictCursor)
    
    #Get cart and currently applied coupon
    curr.execute("""select cart_id ,applied_coupon_id from store_cart
                 where user_id=%s""",(user_id,))
    cart=curr.fetchone()
    cart_id = cart["cart_id"]
    
    # Calculate cart
    summary = get_cart_summary(cart_id, curr)
    curr.close()
    conn.close()
    
    
    return render(request,"cart_page.html",
                   summary)


def apply_coupon(request):
    
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"},
            status=405
        )

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse(
            {"success": False, "message": "Please login first"},
            status=401
        )

    conn = connect()
    from psycopg2.extras import RealDictCursor
    curr = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Get user's cart
        curr.execute("""
            SELECT cart_id
            FROM store_cart
            WHERE user_id = %s
        """, (user_id,))

        cart = curr.fetchone()

        if cart is None:
            return JsonResponse(
                {"success": False, "message": "Cart not found"},
                status=404
            )

        cart_id = cart["cart_id"]
         
        # getting The applied coupon from client
        data = json.loads(request.body)

        code = data.get("code", "").strip().upper()

        if not code:
            return JsonResponse(
            {"success": False, "message": "Enter a coupon code"},
            status=400
        )

        # Find  that coupon in the database
        curr.execute("""
            SELECT
                coupon_id,
                code,
                discount_type,
                discount_value,
                minimum_order,
                maximum_discount,
                is_active,
                expires_at
            FROM store_coupon
            WHERE code = %s
        """, (code,))

        coupon = curr.fetchone()

        # Coupon doesn't exist
        if coupon is None:
            return JsonResponse(
                {"success": False, "message": "Invalid coupon"},
                status=400
            )

        # Coupon is disabled
        if not coupon["is_active"]:
            return JsonResponse(
                {"success": False, "message": "Coupon is inactive"},
                status=400
            )

        # Check expiry
        if coupon["expires_at"] is not None:
            from datetime import datetime, timezone

            if coupon["expires_at"] <= datetime.now(timezone.utc):
                return JsonResponse(
                    {"success": False, "message": "Coupon has expired"},
                    status=400
                )

        # Get current cart summary
        summary = get_cart_summary(cart_id, curr)

        subtotal = summary["subtotal"]

        # Check minimum order
        if subtotal < coupon["minimum_order"]:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"Minimum order value is "
                        f"₹{coupon['minimum_order']}"
                    )
                },
                status=400
            )

        # Apply coupon
        curr.execute("""
            UPDATE store_cart
            SET applied_coupon_id = %s
            WHERE cart_id = %s
        """, (coupon["coupon_id"], cart_id))

        conn.commit()

        # Recalculate using the newly applied coupon
        summary = get_cart_summary(cart_id, curr)

        return JsonResponse({
            "success": True,
            "message": "Coupon applied successfully",
            "code": coupon["code"],
            "discount": str(summary["discount"]),
            "total": str(summary["total"])
        })

    except Exception:
        conn.rollback()
        raise

    finally:
        curr.close()
        conn.close()
        
def remove_coupon(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method"
            },
            status=405
        )

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login first"
            },
            status=401
        )

    conn = connect()
    from psycopg2.extras import RealDictCursor
    curr = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Get user's cart
        curr.execute("""
            SELECT cart_id
            FROM store_cart
            WHERE user_id = %s
        """, (user_id,))

        cart = curr.fetchone()

        if cart is None:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cart not found"
                },
                status=404
            )

        cart_id = cart["cart_id"]

        # Remove applied coupon
        curr.execute("""
            UPDATE store_cart
            SET applied_coupon_id = NULL
            WHERE cart_id = %s
        """, (cart_id,))

        conn.commit()

        # Recalculate cart after removing coupon
        summary = get_cart_summary(cart_id, curr)

        return JsonResponse({
            "success": True,
            "message": "Coupon removed",
            "discount": str(summary["discount"]),
            "total": str(summary["total"])
        })

    except Exception:
        conn.rollback()
        raise

    finally:
        curr.close()
        conn.close()


        
################################
######### ADD TO CART ##########
################################
def add_to_cart(request):
    
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


################################
######### UPDATE CART ##########
################################
def update_cart(request):
    data=json.loads(request.body)
    action=data["action"]
    cart_item_id=data["cart_item_id"]

    conn=connect()
    from psycopg2.extras import RealDictCursor
    curr=conn.cursor(cursor_factory=RealDictCursor)

    # Update quantity
    if(action=="increase"):
        curr.execute("update store_cart_item set quantity=quantity + 1 where cart_item_id=%s returning quantity, product_id",(cart_item_id,))
    else:
        curr.execute("update store_cart_item set quantity=quantity - 1 where cart_item_id=%s returning quantity, product_id",(cart_item_id,))
    row=curr.fetchone()
    quantity=row["quantity"]
    product_id=row["product_id"]

    # Get product price and stock
    curr.execute('select price, stock from "myApp_product" where id=%s',(product_id,))
    product_row=curr.fetchone()
    price=product_row["price"]
    stock=product_row["stock"]

    item_total=price*quantity

    # Get cart_id from this cart_item
    curr.execute("select cart_id from store_cart_item where cart_item_id=%s",(cart_item_id,))
    cart_id=curr.fetchone()["cart_id"]

    # Compute subtotal from all items in the cart
    cart_summary=get_cart_summary(cart_id,curr)

    conn.commit()
    curr.close()
    conn.close()
    return JsonResponse({"quantity":quantity,"item_total":str(item_total),
                         "subtotal":cart_summary["subtotal"],"total":cart_summary["total"],
                         "stock":stock,"discount":cart_summary["discount"]})


################################
###### REMOVE FROM CART ########
################################

def remove_from_cart(request):
    data=json.loads(request.body)
    
    cart_item_id=data["cart_item_id"]
    conn=connect()
    curr=conn.cursor()

    # Get the cart_id before deleting
    curr.execute("select cart_id from store_cart_item where cart_item_id=%s",(cart_item_id,))
    cart_id=curr.fetchone()[0]

    # Delete the item
    curr.execute("delete from store_cart_item where cart_item_id =%s",(cart_item_id,))
    conn.commit()
    curr.close()
    
    from psycopg2.extras import RealDictCursor
    curr=conn.cursor(cursor_factory=RealDictCursor)
    
    cart_summary=get_cart_summary(cart_id,curr)
    items=cart_summary["items"]
    total=cart_summary["total"]
    subtotal=cart_summary["subtotal"]
    discount=cart_summary["discount"]
    coupon=cart_summary["coupon"]
    conn.close()
    
    return JsonResponse({
        "items":items,
        "total":total,
        "subtotal":subtotal,
        "discount":discount,
        "coupon":coupon
    })


def checkout(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return redirect("/signin/")
    
    conn = connect()
    
    #we need a cursor of type 'RealDictCursor' in get_cart_summary(curr) to calculate price and total efficiently
    from psycopg2.extras import RealDictCursor
    curr = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get cart_id for user
    curr.execute("select cart_id from store_cart where user_id=%s", (user_id,))
    cart_row=curr.fetchone()
    cart_id = cart_row["cart_id"]
   
    
    cart_summary=get_cart_summary(cart_id,curr)
    
    return render(request,'checkout.html',cart_summary)
    
    
    
    
    
    
################################
############ LOGOUT ############
################################

def logout(request):
    request.session.flush()
    return redirect("/signin/")

 
def aboutus(request):
    return render(request, "aboutus.html")

def contact_us(request):
    return render(request, "contact_us.html")