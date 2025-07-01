from django.db import models

class User(models.Model):
    login = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=15)
    # profile = models.OneToOneField('Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='user')


class Profile(models.Model):
    name = models.CharField(max_length=20)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name="user"
    )
    avatar = models.CharField(max_length=100)
    last_sign_in = models.DateTimeField(auto_now=True) 
    currency = models.ForeignKey(
        'Currency', 
        on_delete=models.SET_NULL,
        null=True, 
        related_name="currency"
        )
    
    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=20)
    typ = models.BooleanField()
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        null=True
    )
    
    def __str__(self):
        return self.name
    
    
class Operation(models.Model):
    # typ = models.BooleanField()
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category",
        null=True
    )
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    comment = models.CharField(blank=True, null=True, max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    
    
class Currency(models.Model):
    name = models.CharField(max_length=10)
    sign = models.CharField(max_length=3)
    
