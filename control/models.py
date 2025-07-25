from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, login, password=None):
        if not login:
            raise ValueError("Users must have a login")
        user = self.model(login=login)  
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None):
        user = self.create_user(login, password)
        user.is_admin = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser):
    login = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'login'
        
    @property
    def is_staff(self):
        return self.is_admin


    # login = models.CharField(max_length=20, unique=True)
    # password = models.CharField(max_length=15)

    # USERNAME_FIELD = ("login")
    # PASSWORD_FIELD = ("password")


class Profile(models.Model):
    name = models.CharField(max_length=20)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name="profile" ## Replace by profile ?+
    )
    avatar = models.CharField(max_length=100)
    last_sign_in = models.DateTimeField(auto_now=True) 
    currency = models.ForeignKey(
        'Currency', 
        on_delete=models.SET_NULL,
        null=True, 
        related_name="profile_currency" ## Fix ?+
        )
    
    def __str__(self):
        return str(self.id)
        
    

class Category(models.Model):
    name = models.CharField(max_length=20)
    typ = models.BooleanField()
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name="category",
        null=True
    )
    
    def __str__(self):
        return self.name
    
    
class Operation(models.Model):
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="operation", ## FIX ?+
        null=True
    )
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    comment = models.CharField(blank=True, max_length=50)
    date = models.DateTimeField(auto_now_add=True)

        
class Currency(models.Model):
    name = models.CharField(max_length=10)
    sign = models.CharField(max_length=3)



"""
Learn more about SQL Indexes, how they work and how to use them effectively in Django models.
Not need to lean on SQL level, but must understand, how index are helpful for perfomance and how to use them in Django.
"""
