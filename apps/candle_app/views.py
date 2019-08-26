from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *
from datetime import datetime

def index(request):
    print("*"*50, "I am in index")
    return render(request,"candle_app/index.html")

## testing push -- messy
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
        # messages.error(request, "Successfully registered (or logined in)!")
        return redirect("/dashboard")
        # return HttpResponse("sdjyusdy")

def check_login(request):
    print("*"*50, "I am in check_login")
    try:
        user = User.objects.get(email=request.POST['login_email'])  # hm...is it really a good idea to use the get method here?
        if bcrypt.checkpw(request.POST['login_pwd'].encode(), user.password.encode()):
            print("password match")
            request.session['right_user_id']=User.objects.get(email=request.POST['login_email']).id
            print(request.session['right_user_id'])
            return redirect("/dashboard")
            # return HttpResponse("sdkbfilusd")
        else:
            messages.error(request,"failed password")
            return redirect("/")
    except:
        messages.error(request, "Wrong Email!!!")
        return redirect("/")


def dashboard(request):
    print("*"*50, "I am in dashboard")
    if 'right_user_id' not in request.session:
        return redirect("/")
    user=User.objects.get(id=request.session['right_user_id'])
    trip=Trip.objects.all()
    context={
        'user':user,
        'all_trips':trip,
    }
    return render(request,"candle_app/dashboard.html", context)
 

def logoff(request):
    print("*"*50, "I am in logoff")
    if 'right_user_id' not in request.session:
        return redirect("/")
    request.session.clear()
    return redirect("/")


def add(request):
    print("*"*50, "I am in add")
    if 'right_user_id' not in request.session:
        return redirect("/")
    context={
        'user':User.objects.get(id=request.session['right_user_id']),
    }
    # return HttpResponse("dsgfufdsyg")
    return render(request,"candle_app/add.html", context)