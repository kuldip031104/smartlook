from http import client
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import authenticate,login as auth_login
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password




# Create your views here.
def home(request):
    return render(request,"index.html")
def about(request):
    return render(request,"about.html")
def services(request):
    return render(request,"services.html")
def male(request):
    return render(request,"male.html")
def female(request):
    return render(request,"female.html")
def servicesdetails(request):
    return render(request,"services-details.html")

def cart(request):
    user_id = request.session.get("user_id")  

    if not user_id:
        return render(request, "cart.html", {"cart": None, "total_price": 0})  # Show empty cart

    try:
        cart_items = Cart.objects.filter(user_id=user_id).select_related("product__subcategory")  # ✅ Fetch subcategory too

        cart_data = {}
        total_price = 0

        for item in cart_items:
            print("🛍️ Cart Product:", item.product, "Quantity:", item.quantity)  # Debugging

            # ✅ Always fetch the latest price from the Product model
            latest_price = item.product.price  

            # ✅ Get category via subcategory (if exists)
            category = (
                item.product.subcategory.category.name
                if hasattr(item.product.subcategory, "category") and item.product.subcategory.category
                else "Uncategorized"
            )

            # ✅ Check if product already exists in the cart and update quantity
            existing_product = next(
                (p for p in cart_data.get(category, []) if p["id"] == item.product.id),
                None
            )

            if existing_product:
                existing_product["quantity"] += item.quantity  # ✅ Sum quantity
                existing_product["price"] = latest_price * existing_product["quantity"]  # ✅ Recalculate price
            else:
                if category not in cart_data:
                    cart_data[category] = []

                cart_data[category].append({
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": latest_price * item.quantity,  # ✅ Use total price for quantity
                    "quantity": item.quantity,
                    "image": item.product.image.url if item.product.image else "",  
                    "subcategory": item.product.subcategory.name if item.product.subcategory else "N/A",  
                })

            total_price += item.quantity * latest_price  # ✅ Calculate total price correctly

        return render(request, "cart.html", {"cart": cart_data, "total_price": total_price})

    except Exception as e:
        print("❌ Error in cart view:", e)  # ✅ Print error for debugging
        return render(request, "cart.html", {"cart": None, "total_price": 0, "error": str(e)})

# def checkout(request):
#     return render(request,"checkout.html")
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        if name and email and phone and message:
            subject = f"New Contact Inquiry from {name}"
            admin_email = settings.EMAIL_HOST_USER  # Your admin email
            message_body = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            
            Message:
            {message}
            """

            try:
                send_mail(subject, message_body, settings.EMAIL_HOST_USER, [admin_email], fail_silently=False)
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")

        else:
            messages.error(request, "All fields are required!")

        return redirect('contact')
    
    return render(request,"contact.html")

def gallery(request):
    return render(request,"gallery.html")

def logout(request):
    request.session.flush()  # Clears session
    return redirect('/')


def signup(request):
    if request.method == "POST":
        errors = []
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender', '').strip()
        password = request.POST.get('password', '').strip()
        confpass = request.POST.get('confpass', '').strip()

        # Name validation
        if not name:
            errors.append("Name is required.")
        elif len(name) < 3 or len(name) > 50:
            errors.append("Name should be between 3 and 50 characters.")

        # Phone validation
        if not phone:
            errors.append("Phone number is required.")
        else:
            if not phone.isdigit() or len(phone) != 10:
                errors.append("Phone number must be 10 digits.")

        # Gender validation
        valid_genders = ["Male", "Female", "Other"]
        if gender not in valid_genders:
            errors.append("Invalid gender selection.")

        # Email validation
        if not email:
            errors.append("Email is required.")
        else:
            try:
                validate_email(email)
                if UserProfile.objects.filter(email=email).exists():
                    errors.append("Email is already registered.")
            except ValidationError:
                errors.append("Invalid email format.")

        # Password validation
        if not password:
            errors.append("Password is required.")
        else:
            if len(password) < 8 or len(password) > 12:
                errors.append("Password length must be between 8 and 12 characters.")
            if not any(char.isdigit() for char in password):
                errors.append("Password must contain at least one number.")
            if not any(char.isupper() for char in password):
                errors.append("Password must contain at least one uppercase letter.")
            if not any(char in "@_&" for char in password):
                errors.append("Password must contain at least one special symbol (@, _, &).")

        # Confirm password validation
        if not confpass:
            errors.append("Confirm Password is required.")
        elif password != confpass:
            errors.append("Password and Confirm Password do not match.")

        if errors:
            return JsonResponse({"status": "error", "messages": errors})

        try:
            # Save user in UserProfile model
            UserProfile.objects.create(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                password=make_password(password)  # Hash the password before saving
            )
            return JsonResponse({"status": "success", "message": "Account created successfully! Please log in."})

        except Exception as e:
            return JsonResponse({"status": "error", "messages": [f"Error: {e}"]})

    return render(request, "signup.html")


from django.contrib import messages
from django.shortcuts import redirect

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import render
from .models import ProductCategory
from .models import UserProfile  

def login(request):
    print("🚀 Login request received - Method:", request.method)

    if request.method == "GET":
        return render(request, "login.html")  # ✅ Render login page for GET requests

    elif request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            user = UserProfile.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.id
                request.session["user_name"] = user.name
                request.session.modified = True

                return JsonResponse({"status": "success", "message": "Login successful!"})

        except UserProfile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Incorrect email or password!"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        print("this is a form...",form)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "domain": request.get_host(),
                        "site_name": "Your Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "https" if request.is_secure() else "http",
                    }
                    email_body = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                messages.success(request, "Password reset email has been sent.")
                return redirect("password_reset_done")
            else:
                messages.error(request, "No user is associated with this email address.")
    else:
        form = PasswordResetForm()
    return render(request, "registration/password_reset_form.html", {"form": form})




def manageprofile(request):
    if 'user_id' in request.session:
        try:
            user = get_object_or_404(UserProfile, id=request.session['user_id'])  # Get user from DB

            # Ensure session data is accurate
            request.session['user_name'] = user.name
            request.session['user_email'] = user.email
            request.session['user_gender'] = user.gender
            request.session['user_phone'] = user.phone

            context = {
                'username': user.name,
                'email': user.email,
                'gender': user.gender,
                'phone_number': user.phone,
            }

            return render(request, 'manageprofile.html', context)

        except UserProfile.DoesNotExist:
            return redirect("login")  # Redirect if user not found

    return redirect("login")  
    
def edit_prof(request):
    if 'user_id' not in request.session:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("login")

    user = get_object_or_404(UserProfile, id=request.session['user_id'])  # Use UserProfile instead of User

    if request.method == "POST":
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')

        user.email = email
        user.phone = phone_number  # Ensure correct field name
        user.gender = gender  
        user.save()

        # Update session data
        request.session['user_email'] = email
        request.session['user_phone'] = phone_number
        request.session['user_gender'] = gender

        messages.success(request, "Profile updated successfully!")
        return redirect('manageprofile')

    context = {
        'username': user.name,  # Use name instead of username for UserProfile
        'email': user.email,
        'gender': user.gender,
        'phone_number': user.phone,  # Use phone instead of phone_number
    }
    return render(request, 'editprofile.html', context)

    
def product_category(request):
    categories = ProductCategory.objects.all()  # Fetch all categories
    return render(request, 'category.html', {'categories': categories})

def product_sub_category(request, category_name):
    category = get_object_or_404(ProductCategory, name=category_name)
    subcategories = ProductSubcategory.objects.filter(category=category)
    return render(request, 'subcategory.html', {'category': category, 'subcategories': subcategories})

def product(request, subcategory_name):
    subcategory = get_object_or_404(ProductSubcategory, name=subcategory_name)
    product = Product.objects.filter(subcategory=subcategory)
    return render(request, 'product.html', {'subcategory': subcategory, 'product': product})

from .forms import *

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')

    user_id = request.session.get('user_id')  # Get user_id from session
    user = get_object_or_404(UserProfile, id=user_id) if user_id else None

    if request.method == "POST" and user:
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = user  # Assign UserProfile instance
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user': user  # Pass user to template if needed
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserProfile



@csrf_exempt  # Only for testing! Use proper CSRF protection in production
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)

            # ✅ Check if user is logged in (from session)
            user_id = request.session.get("user_id")
            if not user_id:
                return JsonResponse({"success": False, "message": "Unauthorized. Please log in."})

            # ✅ Get UserProfile
            user_profile = UserProfile.objects.get(id=user_id)

            # ✅ Ensure product exists
            product = Product.objects.get(id=product_id)

            # ✅ Add or update cart
            cart_item, created = Cart.objects.get_or_create(
                user=user_profile,  # Use UserProfile
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({"success": True, "message": "Item added to cart!"})

        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found."})

        except UserProfile.DoesNotExist:
            return JsonResponse({"success": False, "message": "User profile not found."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request."})




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cart, UserProfile, Product

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Cart  # Assuming your model is named Cart
from django.db.models import Sum    
from django.db.models import F, Sum

def update_cart(request, cart_id, action):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    
    cart_item = Cart.objects.filter(product=cart_id, user_id=user_id).first()
    if not cart_item:
        return JsonResponse({'error': 'Cart item not found'}, status=404)
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:  # Optional: prevent adding more than stock
            cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif action == 'remove':
        cart_item.delete()
        # ✅ After delete also need correct total
        new_total_price = Cart.objects.filter(user_id=user_id).aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0
        return JsonResponse({'message': 'Item removed', 'removed': True, 'new_total_price': new_total_price})

    cart_item.save()

    # ✅ Correct total calculation
    new_total_price = Cart.objects.filter(user_id=user_id).aggregate(
        total=Sum(F('product__price') * F('quantity'))
    )['total'] or 0

    return JsonResponse({
        'message': 'Cart updated',
        'quantity': cart_item.quantity,
        'new_total_price': new_total_price,
    })

# Function to calculate the total price of all cart items for the user
def get_cart_total_price(user):
    cart_items = Cart.objects.filter(user=user)
    return sum(item.product.price * item.quantity for item in cart_items)



from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from .models import Offer, UserProfile, Cart
from django.utils.timezone import now

def checkout(request):
    user_id = request.session.get("user_id")  # Check authentication manually
    if not user_id:
        return HttpResponse("Unauthorized. Please log in.", status=403)

    try:
        user_profile = UserProfile.objects.get(id=user_id)  
        cart_items = Cart.objects.filter(user=user_profile)

        if not cart_items.exists():
            return HttpResponse("Your cart is empty", status=400)

        # Calculate total for each cart item
        for item in cart_items:
            item.total_price = item.quantity * float(item.product.price)  # Convert to float

        # Calculate total bill amount
        total_amount = sum(item.total_price for item in cart_items)

        # Get the highest available discount offer
        active_offers = Offer.objects.filter(
            offer_start_date__lte=now(), offer_end_date__gte=now()
        ).order_by('-discount_percentage')
        
        discount_percentage = active_offers.first().discount_percentage if active_offers.exists() else 0

        # Calculate total discount
        discounted_amount = (float(total_amount) * discount_percentage) / 100
        final_amount = float(total_amount) - float(discounted_amount)


        context = {
            "name": getattr(user_profile, "name", "Guest"),
            "email": getattr(user_profile, "email", ""),
            "phone": getattr(user_profile, "phone", ""),
            "cart_items": cart_items,
            "total_amount": round(total_amount, 2),
            "discount_percentage": discount_percentage,
            "discounted_amount": round(discounted_amount, 2),
            "final_amount": round(final_amount, 2),
            "offers": active_offers,
        }

        return render(request, 'checkout.html', context)

    except UserProfile.DoesNotExist:
        return HttpResponse("User profile not found.", status=404)
    
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import json
import razorpay
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            final_amount = data.get('final_amount', 0)
            user_id = request.session.get("user_id")

            if not user_id:
                return JsonResponse({"error": "User not logged in"}, status=403)

            amount = int(float(final_amount) * 100)  # Convert to paise

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # ✅ Create Razorpay Order
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })

            # ✅ Simulating Payment Success (Replace this with Razorpay Webhook handling)
            order = create_order(user_id, final_amount)  # Create order in DB
            send_order_confirmation_email(order)  # Send Email after order creation

            return JsonResponse({
                "order_id": razorpay_order.get('id'),
                "amount": amount,
                "user_id": user_id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("Invalid request method.", status=405)


def create_order(user_id, total_price):
    """
    Creates an order and order items from the user's cart.
    """
    user = UserProfile.objects.get(id=user_id)
    order = Order.objects.create(user=user, total_price=total_price, status="Pending")

    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price * item.quantity
        )

    cart_items.delete()  # Clear cart after order creation
    return order


def send_order_confirmation_email(order):
    """
    Sends an order confirmation email with an invoice.
    """
    subject = f"Order Confirmation - #{order.id}"
    recipient_email = order.user.email  # Ensure UserProfile has an 'email' field

    # ✅ Render email template
    context = {"order": order, "items": order.items.all()}
    html_message = render_to_string("emails/order_confirmation.html", context)
    plain_message = strip_tags(html_message)

    # ✅ Send Email
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        html_message=html_message
    )


# salon/views.py

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
def payment_callback(request):
    payment_id = request.GET.get("payment_id")
    order_id = request.GET.get("order_id")
    user_id = request.session.get("user_id")

    if not payment_id or not order_id:
        return JsonResponse({"error": "Invalid payment details"}, status=400)

    try:
        user_profile = get_object_or_404(UserProfile, id=user_id)
        cart_items = Cart.objects.filter(user=user_profile)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty. Order cannot be placed."}, status=400)

        # Calculate final amount
        total_amount = sum(item.quantity * item.product.price for item in cart_items)

        # Apply discount if available
        active_offers = Offer.objects.filter(
            offer_start_date__lte=now(), offer_end_date__gte=now()
        ).order_by('-discount_percentage')

        discount_percentage = active_offers.first().discount_percentage if active_offers.exists() else 0
        discounted_amount = (float(total_amount) * discount_percentage) / 100
        final_amount = float(total_amount) - float(discounted_amount)

        # ✅ Save Order
        new_order = Order.objects.create(
            user=user_profile,
            total_price=final_amount,
            status="Processing",  # Payment is successful, so order is processing
            phone_number=user_profile.phone,
            discount_applied=discount_percentage,
        )

        # ✅ Save Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # ✅ Clear Cart After Order
        cart_items.delete()

        return render(request, "payment_success.html", {"order": new_order})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def offers_view(request):
    offers = Offer.objects.prefetch_related('products').all()  # ✅ Optimize DB Query
    return render(request, "offers.html", {"offers": offers})

def service_category(request):
    categories = ServiceCategory.objects.all()  # Fetch all categories
    return render(request, 'servicecategory.html', {'categories': categories})

def service_sub_category(request, category_name):
    category = get_object_or_404(ServiceCategory, name=category_name)
    subcategories = ServiceSubcategory.objects.filter(category=category).prefetch_related('services')
    return render(request, 'servicesubcategory.html', {'category': category, 'subcategories': subcategories})

def services(request, subcategory_name):
    subcategory = get_object_or_404(ServiceSubcategory, name=subcategory_name)
    services = Service.objects.filter(subcategory=subcategory)
    return render(request, 'service_list.html', {'subcategory': subcategory, 'services': services})

from django.http import JsonResponse
from django.views import View
from .models import Stylist

class StylistListView(View):
    def get(self, request):
        stylists = Stylist.objects.filter(is_available=1).values('id', 'name', 'is_available')
        print("this is s stylis.....",stylists)
        return JsonResponse(list(stylists), safe=False)

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime, time
from .models import Stylist, Slot, Appointment
from django.shortcuts import get_object_or_404
import json

class SlotGenerator:
    @staticmethod
    def generate_slots():
        """Generate default slots for available stylists."""
        today = timezone.localdate()
        next_month = today + timedelta(days=30)
        time_slots = [
            (time(hour=10, minute=0), time(hour=11, minute=0)),
            (time(hour=11, minute=0), time(hour=12, minute=0)),
            (time(hour=12, minute=0), time(hour=13, minute=0)),
            (time(hour=13, minute=0), time(hour=14, minute=0)),
            (time(hour=14, minute=0), time(hour=15, minute=0)),
            (time(hour=15, minute=0), time(hour=16, minute=0)),
            (time(hour=16, minute=0), time(hour=17, minute=0)),
        ]

        for stylist in Stylist.objects.filter(is_available=True):
            for day in range(31):  # Next 30 days including today
                date = today + timedelta(days=day)
                for start, end in time_slots:
                    Slot.objects.get_or_create(
                        stylist=stylist, date=date, start_time=start, end_time=end
                    )

class AvailableSlotsView(View):
    def get(self, request, stylist_id, date):
        """Fetch available slots for a specific stylist and date."""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format"}, status=400)

        print("Requested Date:", date_obj)

        if date_obj < timezone.localdate():
            return JsonResponse({"error": "Cannot book past dates"}, status=400)

        now = timezone.localtime()
        
        if date_obj == now.date():
            # Limit slots to 3 hours ahead for today's bookings
            min_time = (now + timedelta(hours=3)).time()
            slots = Slot.objects.filter(
                stylist_id=stylist_id, date=date_obj, is_booked=False, start_time__gte=min_time
            )
        else:
            slots = Slot.objects.filter(stylist_id=stylist_id, date=date_obj, is_booked=False)

        slots_data = [{"id": slot.id, "start_time": slot.start_time.strftime("%H:%M")} for slot in slots]

        if not slots_data:
            return JsonResponse({"message": "No available slots"}, status=200)  # Return empty list instead of 400

        return JsonResponse(slots_data, safe=False)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from datetime import timedelta
import json
from django.core.mail import send_mail
from .models import Appointment, Slot, Stylist, ServiceCategory, ServiceSubcategory
import razorpay
from django.db import models, transaction
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from django.http import JsonResponse


from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

@transaction.atomic
def book_appointment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        stylist = get_object_or_404(Stylist, id=request.POST.get("stylist_id"))
        slot = get_object_or_404(Slot, id=request.POST.get("slot_id"), is_booked=False)
        service_category = get_object_or_404(ServiceCategory, id=request.POST.get("category_id"))
        service_subcategory = get_object_or_404(ServiceSubcategory, id=request.POST.get("subcategory_id"), category=service_category)

        now = timezone.localtime()
        if slot.date < now.date() or (slot.date == now.date() and slot.start_time < (now + timedelta(hours=3)).time()):
            return JsonResponse({"error": "Invalid slot selection"}, status=400)

        # Create Appointment
        appointment = Appointment.objects.create(
            name=name, email=email, phone_number=phone,
            stylist=stylist, date=slot.date, slot=slot,
            service_category=service_category, service_subcategory=service_subcategory
        )

        # Mark slot as booked
        slot.is_booked = True
        slot.save()

        # Send Confirmation Email
        subject = "Your Salon Appointment is Confirmed"
        message = f"""
Dear {name},

Your appointment with {stylist.name} for {service_category.name} - {service_subcategory.name} 
has been successfully booked.

📅 Date: {slot.date.strftime('%d-%m-%Y')}
⏰ Time: {slot.start_time.strftime('%I:%M %p')}
💇 Stylist: {stylist.name}

Thank you for choosing us!

Best Regards,
Salon Team
"""
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        return JsonResponse({"message": "Appointment booked successfully!"})

    categories = ServiceCategory.objects.all()
    stylists = Stylist.objects.filter(is_available=True)
    return render(request, "appointment.html", {"categories": categories, "stylists": stylists})


@transaction.atomic
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        payment = get_object_or_404(razorpay.Payment, payment_id=order_id)
        appointment = payment.appointment

        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        payment.status = 'Success'
        payment.save()

        appointment.slot.is_booked = True
        appointment.slot.save()

        send_mail("Appointment Confirmation", f"Hello {appointment.name}, your appointment is booked.", "kroyalsalon1@gmail.com", [appointment.email])

        return render(request, "book_appointment.html", {"success": "Payment successful! Appointment booked."})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ServiceCategory, ServiceSubcategory

def get_service_subcategories(request, category_id):
    """Fetch subcategories based on the selected service category."""
    subcategories = ServiceSubcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ServiceCategory, ServiceSubcategory

def get_filtered_subcategories(request, category_id):
    """Fetch only the subcategories belonging to the selected service category."""
    subcategories = ServiceSubcategory.objects.filter(category_id=category_id).values('id', 'name')
    print("this is a subcategory..........",subcategories)
    if not subcategories:
        return JsonResponse({"error": "No subcategories found for the selected category"}, status=400)

    return JsonResponse(list(subcategories), safe=False)

def delete_cart_item(request, cart_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    try:
        cart_item = Cart.objects.get(product=cart_id, user_id=user_id)
        cart_item.delete()
        return JsonResponse({'message': 'Cart item deleted successfully'})
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)
    
@csrf_exempt
def delete_all_cart_items(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    Cart.objects.filter(user_id=user_id).delete()
    return JsonResponse({'message': 'All cart items deleted successfully'})