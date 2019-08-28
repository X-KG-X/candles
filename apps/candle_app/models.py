from __future__ import unicode_literals
from django.db import models
import re
from datetime import datetime

# Create your models here.

class loginManager(models.Manager):
    def login_validator(self, postData):
        errors={}
        if len(postData['f_name'])==0:
            errors['f_name']="Need first name"        
        elif len(postData['f_name'])<2:
            errors['f_name']="First name should be at least 2 characters"

        if len(postData['l_name'])==0:
            errors['l_name']="Need last name"            
        elif len(postData['l_name'])<2:
            errors['l_name']="Last name should be at least 3 characters"

        if User.objects.filter(email=postData['register_email']):
            errors['dup_email']="Email already exists, user another email"
        if not re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$').match(postData['register_email']):
            errors['register_email']="Enter valid email address"
        if  len(postData['register_pwd'])<8:
            errors['register_pwd']="Password needs to be at least 8 characters"
        elif postData['register_pwd'] !=postData['confirm_pwd']:
            errors['match_pwd']="Passwords should match"
        return errors


class User(models.Model):
    first_name=models.CharField(max_length=45)
    last_name=models.CharField(max_length=45)
    seller=models.BooleanField(default=False)
    email=models.CharField(max_length=45)
    password=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=loginManager() 

class Product(models.Model) :
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.TextField()
    fragrance = models.CharField(max_length=255)
    size = models.CharField(max_length=45)
    inventory = models.IntegerField() # keep track of number of items we have
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Order(models.Model) :
    cart_id = models.PositiveIntegerField()
    user= models.ForeignKey(User, related_name="order")
    product = models.ForeignKey(Product, related_name="product")
    quantity=models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class History(models.Model) :
    user= models.ForeignKey(User, related_name="order_h")
    product = models.ForeignKey(Product, related_name="product_h")
    quantity=models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    