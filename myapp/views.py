from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Product, Cart, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from rapidfuzz import fuzz
from django.db.models.functions import Lower, Trim
from django.db.models import Sum

# Create your views here.

@login_required(login_url='login')
def index(request):

    search = request.GET.get('search', '').strip()
    data = Product.objects.all()

    total_product = 0
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    
        for item in cart_items:
         total_product += item.quantity
    

    if search:
        products = list(data)
        
        result = []
        
        for product in products:
        
            score = fuzz.WRatio(
            search.lower(),
            product.name.lower()
            )
        
            if score >= 60:
              result.append((product, score))
        
            
            result.sort(key=lambda x: x[1], reverse=True)
        
            data = [product for product, score in result]

    return render(request, 'index.html', {'data': data, 'total_product': total_product})



@login_required(login_url='login')
def product(request):
    if request.method == "POST":
        name = request.POST.get('name').strip()
        location = request.POST.get('location')

        date = request.POST.get('date')
        expired = request.POST.get('expired')

        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        discount = request.POST.get('discount') or 0

        image = request.FILES.get('image')
        exists = Product.objects.annotate(
            clean_name=Trim(Lower('name'))
        ).filter(
            clean_name=name.lower()
        ).first()

        if exists:
            messages.error(request, f"{exists.name} already exists!")
            return redirect('edit', id=exists.id)
        
        Product.objects.create(name=name, location=location, date=date, 
        expired=expired, quantity=quantity, price=price, discount=discount, image=image)
        messages.success(request, 'Product Successfully Added')
        return redirect('product')
        
    return render(request, 'product.html')

@login_required(login_url='login')
def listproduct(request):
    search = request.GET.get('search', '').strip()
    data = Product.objects.all()

    if search:
            products = list(data)
    
            result = []
    
            for product in products:
    
                score = fuzz.WRatio(
                    search.lower(),
                    product.name.lower()
                )
    
                if score >= 60:
                    result.append((product, score))
    
        
            result.sort(key=lambda x: x[1], reverse=True)
    
            data = [product for product, score in result]

    paginator = Paginator(data, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'listproduct.html', {'data': page, 'page': page, 'search': search})


def increase_quantity(request, id):
    product = Product.objects.get(id=id)

    product.quantity += 1
    product.save()

    return redirect('listproduct')


def decrease_quantity(request, id):
    product = Product.objects.get(id=id)

    if product.quantity > 0:
        product.quantity -= 1
        product.save()

    return redirect('listproduct')


@login_required(login_url='login')
def delete(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.success(request, 'Deleted Successfully')
    return redirect('listproduct')


@login_required(login_url='login')
def edit(request, id):
    product = Product.objects.get(id=id)
    if request.method == "POST":
        product.name = request.POST.get('name')
        product.location = request.POST.get('location')
    
        product.date = request.POST.get('date')
        product.expired = request.POST.get('expired')
    
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.discount = request.POST.get('discount')

        if request.FILES.get('image'):
           product.image = request.FILES.get('image')
        product.save() 
        messages.success(request, 'Update Successfilly!')
        
        return redirect('listproduct')
    return render(request, 'edit.html', {'product': product})


def userlogout(request):
    logout(request)
    return redirect('index')


def userlogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect("index")

            else:
                messages.error(request, "Password is incorrect.")

        except User.DoesNotExist:
            messages.error(request, "Email is incorrect.")

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('password')
        con_password = request.POST.get('con_password')

        if password != con_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, 'Registration successful')
        return redirect('login')
    return render(request, 'register.html')


@login_required(login_url='login')
def addcart(request, id):
    product = Product.objects.get(id=id)

    cart = Cart.objects.filter(
        user=request.user,
        product=product
    ).first()

    if cart:
        cart.quantity += 1
        cart.save()

    else:
        cart = Cart(
            user=request.user,
            product=product,
            quantity=1
        )
        cart.save()

    return redirect('index')


@login_required(login_url='login')
def mycart(request):

    cart_items = Cart.objects.filter(user=request.user)

    total_product = 0
    total_price = 0

    for item in cart_items:
        total_product += item.quantity
        total_price += item.product.price * item.quantity


    return render(request, 'mycart.html', {
        'cart_items': cart_items,
        'total_product': total_product,
        'total_price': total_price,
    })


def cart_quantity_pluss(request, id):

    cart_item = Cart.objects.get(id=id)

    cart_item.quantity = cart_item.quantity + 1
    cart_item.save()

    return redirect('mycart')



def cart_quantity_minuss(request, id):

    cart_item = Cart.objects.get(id=id)

    if cart_item.quantity > 1:
        cart_item.quantity = cart_item.quantity - 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('mycart')



def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('mycart')

    total_product = 0
    total_price = 0

    for item in cart_items:
        total_product += item.quantity
        total_price += item.product.price * item.quantity

    if request.method == "POST":

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not name or not phone or not address:
            messages.error(request, "Please fill in all information.")
            return redirect('checkout')

        # Order create
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            total_product=total_product,
            total_price=total_price
        )

        # Order items save
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Stock কমানো
            if item.product.quantity >= item.quantity:
                item.product.quantity -= item.quantity
                item.product.save()

            else:
                messages.error(
                    request,
                    f"{item.product.name} stock is not available."
                )
                order.delete()
                return redirect('mycart')

        # Cart empty
        cart_items.delete()

        messages.success(
            request,
            f"Order #{order.id} placed successfully!"
        )

        return redirect('order_success', id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_product': total_product,
        'total_price': total_price,
    })

@login_required(login_url='login')
def order_success(request, id):

    order = Order.objects.get(
        id=id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order
    })



