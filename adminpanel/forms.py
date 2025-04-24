from django import forms
from home.models import *  # Import the Category model from the home app
import io
from reportlab.pdfgen import canvas

class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'image']  # Add all the fields you want to manage
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = ProductSubcategory
        fields = ['name', 'category', 'image']  # Include image field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'subcategory','description', 'price', 'image', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Name'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'description':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Price'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stock Quantity'}),
        }
        
class DiscountForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'offer_start_date', 'offer_end_date', 'discount_percentage']  # Removed offer_desc

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter offer title'}),
            'offer_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'offer_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount percentage'}),
        }

        labels = {
            'title': 'Offer Title',
            'offer_start_date': 'Offer Start Date',
            'offer_end_date': 'Offer End Date',
            'discount_percentage': 'Discount Percentage',
        }

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError("Discount percentage must be between 0 and 100.")
        return discount

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'total_price', 'status', 'address', 'phone_number', 'discount_applied', 'cancellation_reason', 'return_reason']
        widgets = {
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cancellation_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'return_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

def generate_pdf(orders):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 800, "Order Report")

    y_position = 780
    for order in orders:
        pdf.drawString(100, y_position, f"Order ID: {order.id}, Customer: {order.user}, Total: {order.total_price}")
        y_position -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

        


class StylistForm(forms.ModelForm):
    class Meta:
        model = Stylist
        fields = ['name', 'is_available']
        
class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ['stylist', 'date', 'start_time', 'end_time', 'is_booked']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'image']

class ServiceSubcategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceSubcategory
        fields = ['name', 'category']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'subcategory']

from django import forms
from home.models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone_number', 'stylist', 'date', 'slot', 'service_category', 'service_subcategory']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'slot': forms.Select(),
        }
