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


# class tripManager(models.Manager):
#     def trip_validator(self, postData):
#         errors={}
#         if len(postData['place'])==0:
#             errors['place']="Need destination name"        
#         elif len(postData['place'])<3:
#             errors['place']="Destination should be at least 3 characters"

#         if not postData['start']:
#             errors['start']="Need start date"            
#         elif datetime.strptime(postData['start'],'%Y-%m-%d')< datetime.now():
#             errors['start']="start date should be in the future"

#         if not postData['end']:
#             errors['end']="Need end date"            
#         if postData['end']< postData['start']:
#             errors['date']="end date should be after start date"

#         if len(postData['plan'])==0:
#             errors['plan']="Need plan"        
#         elif len(postData['plan'])<3:
#             errors['plan']="Plan should be at least 3 characters"
#         return errors


class User(models.Model):
    first_name=models.CharField(max_length=45)
    last_name=models.CharField(max_length=45)
    email=models.CharField(max_length=45)
    password=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=loginManager() 

# class Trip(models.Model):
#     place=models.CharField(max_length=45)
#     start=models.DateField()
#     end=models.DateField()
#     plan=models.CharField(max_length=255)
#     joined_by=models.ForeignKey(User, related_name="joined", null=True)
#     added_by=models.ForeignKey(User, related_name="trip")
#     trip_goers=models.ManyToManyField(User, related_name="trip_joined")
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now=True)
#     objects=tripManager() 

# Product
# class ProductManager(models.Manager) :
#     def validator(self, postData):
#         errors={}
        # name
        # if len(postData['name'])==0:
        #     errors['name']="Product name is a required field"        
        # elif len(postData['name'])<5:
        #     errors['name']="Product name should be at least 5 characters"

        # price
        # if len(postData['price'])==0:
        #     errors['price']="Price is a required field"        
        # elif postData['price']<0:
        #     errors['price']="No free items here ...this is a business"
        # description
        # return errors


class Product(models.Model) :
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.TextField()
    fragrance = models.ForeignKey(Fragrance, related_name="products")
    size = models.ForeignKey(Size, related_name="products")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Fragrance(models.Model) :
    name = models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Size(models.Model) :
    name = models.CharField(max_length=45)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)   
