from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *
from datetime import datetime
from django.db.models import Q, Sum, Min, F
import random, string

from django.core.mail import send_mail
from django.conf import settings


def index(request):
    print("*"*50, "I am in index")
    return render(request,"candle_app/index.html")

# registration
def check_registration(request):
    print("*"*50, "I am in index")
    errors=User.objects.login_validator(request.POST)
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/")
    else:
        right_user=User.objects.create(first_name=request.POST['f_name'],last_name=request.POST['l_name'], email=request.POST['register_email'],password=bcrypt.hashpw(request.POST['register_pwd'].encode(), bcrypt.gensalt()))
        request.session['right_user_id']=right_user.id
        request.session['cart_id']=1
        # messages.error(request, "Successfully registered (or logined in)!")
        return redirect("/dashboard")
        # return HttpResponse("sdjyusdy")

# login
def check_login(request):
    print("*"*50, "I am in check_login")
    try:
        user = User.objects.get(email=request.POST['login_email'])  # hm...is it really a good idea to use the get method here?
        if bcrypt.checkpw(request.POST['login_pwd'].encode(), user.password.encode()):
            print("password match")
            request.session['right_user_id']=User.objects.get(email=request.POST['login_email']).id
            print(request.session['right_user_id'])
            if user.order.all().count()<1:
                request.session['cart_id']=1
            else:
                request.session['cart_id']=user.order.last().id+1
            return redirect("/dashboard")
            # return HttpResponse("sdkbfilusd")
        else:
            messages.error(request,"failed password")
            return redirect("/")
    except:
        messages.error(request, "Wrong Email!!!")
        return redirect("/")

# dashboard - all the products in our inventories
def dashboard(request):
    print("*"*50, "I am in dashboard")
    if 'right_user_id' not in request.session:
        print ("right user id not exist!!")
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    product=Product.objects.all()
    context={
        'user':user,
        'all_products':product,
        'range' : range(1,11),
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 
    } 
    return render(request,"candle_app/dashboard.html", context)
 
# logoff. not deleting items in the cart even after loggin out
def logoff(request):
    print("*"*50, "I am in logoff")
    if 'right_user_id' not in request.session:
        return redirect("/")
    # Order.objects.all().delete()
    request.session.clear()
    return redirect("/")

# detail - shows product detail when user clicks it.
def detail(request, product_id):
    print("*"*50, "I am in detail")
    if 'right_user_id' not in request.session:
        return redirect("/") 
    user = User.objects.get(id=request.session['right_user_id'])
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    context={
        'product': Product.objects.get(id=product_id),
        'user':User.objects.get(id=request.session['right_user_id']),
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0,
        'range' : range(1,11),
    }
    return render(request, "candle_app/detail.html", context)

# add - add items to cart
def add(request, product_id):
    print("*"*50, "I am in add")
    if 'right_user_id' not in request.session:
        return redirect("/")
    quantity=request.POST['quantity']
    user=User.objects.get(id=request.session['right_user_id'])
    product=Product.objects.get(id=product_id)
    # add items to the cart
    Order.objects.create(cart_id=request.session['cart_id'], user=user, product=product, quantity=quantity)
    
    # # keep track of stocks in the product table
    # product.inventory = product.inventory - int(quantity)
    # product.save()
    # print("product:", product.name, product.inventory)
    # MOVE TO DO IN update_select_options

    # keep track of number of items in the cart
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    context = {'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 }
    print ("context: ", context)
    return render(request, 'candle_app/partials/num_items_cart.html', context)
    # return redirect("/dashboard")

def update_select_options(request, product_id) :
    if 'right_user_id' not in request.session:
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    product=Product.objects.get(id=product_id)
    
    # keep track of stocks in the product table
    quantity=request.POST['quantity']
    product.inventory = product.inventory - int(quantity)
    product.save()
    print("product:", product.name, product.inventory)

    context={
        'user':user,
        'product':product,
        'range' : range(1,11),
    } 
    return render(request,"candle_app/partials/update_select_options.html", context)

# cart - show items in the cart
def cart(request):
    print("*"*50, "I am in cart")
    if 'right_user_id' not in request.session:
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    orders=Order.objects.filter(user=user)
    total=0.0
    for order in orders:
        total += order.quantity*order.product.price
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    
    # orders in the cart - group by product name / product size / fragrance and shows summed quantity, ..
    orders_grouped = orders.values('product__id', 'product__name', 'product__size', 'product__fragrance').annotate(num_q=Sum('quantity'), 
                price=Min('product__price'),sub_total=Sum(F('quantity')*F('product__price')))
    context={
        # 'orders':orders,
        'orders_grouped' : orders_grouped,
        'user':user,
        'total':f"${total}",
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 
    }
    return render(request,"candle_app/cart.html", context)

# history - show order (purchased) history
def history(request):
    print("*"*50, "I am in history")
    if 'right_user_id' not in request.session:
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    # user_orders=History.objects.filter(user=user)
    
    # collect order information by history_id
    # history_ids = History.objects.all().values_list('history_id').distinct()
    history_ids = History.objects.filter(user=user).values_list('history_id').distinct()
    history_order_set = []
    for history_id in history_ids :
        history_id = history_id[0] # get unique history id

        # get items ordered under history_id
        orders = History.objects.filter(history_id=history_id, user=user)
        orders_set = []
        total_price = 0.0
        for order in orders :
            subtotal_price = (order.quantity * order.product.price)
            product_name_with_size = f"{order.product.name} ({order.product.size})"
            orders_set.append((product_name_with_size, order.quantity, subtotal_price))
            total_price += subtotal_price

        history_order_set.append({"history_id" : history_id, 
                        "orders_set" : orders_set,
                        "total_price" : total_price,
                        "created_at" : order.created_at
                        })
    # sort by created_at
    history_order_set = sorted(history_order_set, key=lambda i : i['created_at'], reverse=True)
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
 
    context={
        'user':user,
        # 'user_histories':user_histories
        'history_order_set' : history_order_set,
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 
    }
    return render(request,"candle_app/history.html", context)

# remove - remove from the cart
def remove(request, product_id):
    print("*"*50, "I am in cart")
    if 'right_user_id' not in request.session:
        return redirect("/")
    user = User.objects.get(id=request.session['right_user_id'])
    orders=Order.objects.filter(product=Product.objects.get(id=product_id), user=user)
    back_inventory = orders.aggregate(s=Sum('quantity'))['s']
    orders.delete()

    # put the quantity back to the inventory
    product = Product.objects.get(id=product_id)
    product.inventory = product.inventory + back_inventory
    product.save()
    print("product:", product.name, product.inventory)

    return redirect("/cart")

# search keyword from search bar in product database
def search_item(request) :
    if 'search' not in request.POST :
        return redirect("/dashboard")

    keyword = request.POST['search'].lower()
    user=User.objects.get(id=request.session['right_user_id'])

    if (keyword == "") :
        return redirect("/dashboard")

    keyword_list = keyword.split()
    keyword_complete = keyword_list[0:len(keyword_list)-1]
    keyword_incomplete = keyword_list[len(keyword_list)-1]

    # get products has typed_incomplete in their name
    product_candidates = Product.objects.filter(Q(name__icontains=keyword_incomplete) | Q(size__icontains=keyword_incomplete))

    product_result = []
    # for each candidates - check if it has all the word in typed_complete
    for product in product_candidates :
        p_name = product.name + " " + product.size
        if (productStringContains(p_name, keyword_complete)) :
            product_result.append(product)

    num_search = len(product_result)
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    context = {
        'user':user,
        'keyword' : keyword,
        'num_search' : num_search,
        'products_list' : product_result,
        'range' : range(1,11),
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 
    }
    return render(request, "candle_app/dashboard_searched.html", context)

# search result while typing - AJAX
def search_ajax(request) :
    typed = request.POST['search'].lower()

    if (len(typed) == 0) :
        context = {"products_list" : Product.objects.all(), 'range': range(1,11)}
        return render(request, 'candle_app/search_ajax_img.html', context)

    typed_list = typed.split()
    typed_complete = typed_list[0:(len(typed_list)-1)]
    typed_incomplete = typed_list[len(typed_list)-1]

    # get products has typed_incomplete in their name
    product_candidates = Product.objects.filter(Q(name__icontains=typed_incomplete) | Q(size__icontains=typed_incomplete))

    product_result = []
    # for each candidates - check if it has all the word in typed_complete
    for product in product_candidates :
        p_name = product.name + " " + product.size
        if (productStringContains(p_name, typed_complete)) :
            product_result.append(product)

    context = {"products_list" : product_result, 'range': range(1,11)}
    return render(request, 'candle_app/search_ajax_img.html', context)

# helper function for checking a product has list of strings in their name
def productStringContains(string, word_list) :
    # check if string contains all the word in word_list
    string = string.lower()
    string_list = string.split()
    for word in word_list :
        if not word in string_list :
            return False
    return True

# buy - 
def buy(request):
    print("*"*50, "I am in buy")
    if 'right_user_id' not in request.session:
        return redirect("/")
    user = User.objects.get(id=request.session['right_user_id'])

    # create a unique history id to be able to keep track of items ordered (purchased) at once
    purchased_at = str(datetime.now())
    history_id = f"{user.id}_{purchased_at}_{randomword(10)}"
    while (True) :
        history_with_id = History.objects.filter(history_id=history_id)
        if (len(history_with_id) == 0) :
            break
        # create another history id
        history_id = f"{user.id}_{purchased_at}_{randomword(10)}"

    # for order in Order.objects.all():
    for order in Order.objects.filter(user=user) :
        History.objects.create(history_id=history_id, user=user, product=order.product, quantity=order.quantity)

     #send confirmation email
    subject = 'Thank you for your purchase'
    message = 'It means a world to us that you have chosen our Brand! Enjoy our Candles. Thank you again!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list )
        
    # Order.objects.all().delete()
    Order.objects.filter(user=user).delete()
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    context={
        'user': user,
        'num_items_in_cart':num_items_in_cart if num_items_in_cart != None else 0 
    }
    return render (request,"candle_app/confirm.html", context)

# helper function to generate a random string
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

# google login - test
def google_login(request) :
    print ("## I'm in google login test")
    print (request)
    print ("email:", request.GET['email'])
    print ("name:",request.GET['name'])
    email = request.GET['email']
    name = request.GET['name']

    name_list = name.split()
    first_name = name_list[0]
    last_name = "XX"
    
    if (len(name_list) > 1) :   
        last_name = name_list[1]

    user = User.objects.filter(email=email)
    if (not user) :
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=randomword(8)
        )
        request.session['right_user_id'] = user.id
        request.session['cart_id']=1
        print (request.session['right_user_id'])
        # return redirect('/dashboard')'
        return HttpResponse("anything")
    else : 
        request.session['right_user_id'] = user[0].id
        request.session['cart_id']=1
        print (request.session['right_user_id'])
        # return redirect('/dashboard')
        return HttpResponse("anything")
    # return HttpResponse("testing")