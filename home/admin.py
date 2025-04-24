from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'gender')
    search_fields = ('name', 'email', 'phone')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image_preview")
    search_fields = ("name",)
    ordering = ("id",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return "No Image"
    
    image_preview.short_description = "Image Preview"

@admin.register(ProductSubcategory)
class ProductSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "image_preview")
    search_fields = ("name", "category__name")
    list_filter = ("category",)
    ordering = ("id",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return "No Image"
    
    image_preview.short_description = "Image Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subcategory", "price", "stock", "image_preview", "created_at", "updated_at")
    search_fields = ("name", "subcategory__name")
    list_filter = ("subcategory", "created_at")
    ordering = ("id",)
    list_editable = ("price", "stock")  # Allow inline editing

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return "No Image"
    
    image_preview.short_description = "Image Preview"

# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ("name", "email", "phone", "barber", "date", "time", "selection_type")
#     list_filter = ("date", "selection_type", "barber", "gender")
#     search_fields = ("name", "email", "phone", "barber")
#     ordering = ("-date", "time")  # Latest appointments first

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')  # ✅ Use lowercase
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')  # ✅ Fix search fields
    ordering = ('id',)

admin.site.register(Cart, CartAdmin)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image_preview")
    search_fields = ("name",)
    ordering = ("id",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return "No Image"
    
    image_preview.short_description = "Image Preview"
    

@admin.register(ServiceSubcategory)
class ServiceSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ("name", "category__name")
    list_filter = ("category",)
    ordering = ("id",)
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subcategory")
    search_fields = ("name", "subcategory__name")
    list_filter = ("subcategory",)
    ordering = ("id",)
    

    # from django.contrib import admin
from django.contrib import admin
from .models import Stylist, Slot, Appointment

@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('stylist', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'stylist', 'date', 'slot')
    list_filter = ('date', 'stylist')
    search_fields = ("name", "email", "phone", "stylist")
