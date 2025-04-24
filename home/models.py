from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserProfileManager(BaseUserManager):
    def create_user(self, name, email, password=None, **extra_fields):
        if not name:
            raise ValueError("The Name field is required")
        if not email:
            raise ValueError("The Email field is required")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(name, email, password, **extra_fields)

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class ProductSubcategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

from django.utils.timezone import now

class Offer(models.Model):
    title = models.CharField(max_length=255)
    discount_percentage = models.FloatField(default=0)
    offer_start_date = models.DateTimeField(default=now)  # Default to current time
    offer_end_date = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.offer_start_date <= now() <= self.offer_end_date if self.offer_end_date else True

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}%"

class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - {self.user.email}"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='s_category_images/', blank=True, null=True)

    def _str_(self):
        return self.name
        
class ServiceSubcategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name
    
class Service(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.CASCADE, related_name='services',null=True)

    def __str__(self):
        return self.name
    

from django.db import models

from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime

class Stylist(models.Model):
    name = models.CharField(max_length=255, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Slot(models.Model):
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.stylist.name} - {self.date} {self.start_time} to {self.end_time}"

class Appointment(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE)
    date = models.DateField()
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE)
    
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE,null=True)
    service_subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"Appointment for {self.name} with {self.stylist.name} on {self.date}"



class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Ratings from 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.product.name} by {self.user.user_name}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ADD MISSING FIELDS
    discount_applied = models.FloatField(default=0, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    return_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.name} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
