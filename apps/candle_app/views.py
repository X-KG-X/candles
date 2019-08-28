from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *
from datetime import datetime
from django.db.models import Q, Sum
import random, string

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
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    product=Product.objects.all()
    context={
        'user':user,
        'all_products':product,
        'range' : range(1,11),
        'num_items_in_cart' : num_items_in_cart
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
    context={
        'product': Product.objects.get(id=product_id),
        'user':User.objects.get(id=request.session['right_user_id']),
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
    num_items_in_cart = Order.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    context = {"num_items_in_cart":num_items_in_cart}
    print ("context: ", context)
    return render(request, 'candle_app/partials/num_items_cart.html', context)
    # return redirect("/dashboard")

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
    context={
        'orders':orders,
        'user':user,
        'total':f"${total}",
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
    history_ids = History.objects.all().values_list('history_id').distinct()
    history_order_set = []
    for history_id in history_ids :
        history_id = history_id[0] # get unique history id

        # get items ordered under history_id
        orders = History.objects.filter(history_id=history_id)
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
    context={
        'user':user,
        # 'user_histories':user_histories
        'history_order_set' : history_order_set
    }
    return render(request,"candle_app/history.html", context)

# remove - remove from the cart
def remove(request, order_id):
    print("*"*50, "I am in cart")
    if 'right_user_id' not in request.session:
        return redirect("/")
    order=Order.objects.get(id=order_id)
    order.delete()
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
    context = {
        'user':user,
        'keyword' : keyword,
        'num_search' : num_search,
        'products_list' : product_result,
        'range' : range(10),
    }
    return render(request, "candle_app/dashboard_searched.html", context)

# search result while typing - AJAX
def search_ajax(request) :
    typed = request.POST['search'].lower()

    if (len(typed) == 0) :
        context = {"products_list" : Product.objects.all(), 'range': range(10)}
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

    context = {"products_list" : product_result, 'range': range(10)}
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
    context={
        'user': user
    }

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
    # Order.objects.all().delete()
    Order.objects.filter(user=user).delete()
    return render (request,"candle_app/confirm.html", context)
   

# helper function to generate a random string
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))