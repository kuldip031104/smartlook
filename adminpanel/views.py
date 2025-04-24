from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from home.models import *
from django.db.models import Sum
from adminpanel.forms import * # Import the form
from django.core.paginator import Paginator  # For pagination
from django.utils import timezone



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the user is a staff member or superuser (admin)
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')  # redirect to the admin dashboard
            else:
                error_message = "You do not have permission to access the admin panel."
                return render(request, 'admin/login.html', {'error': error_message})
        else:
            error_message = "Invalid username or password"
            return render(request, 'admin/login.html', {'error': error_message})
    
    return render(request, 'admin/login.html')

from django.contrib.auth import logout

def admin_logout(request):
    logout(request)  # Logs out the current user
    return redirect('admin_login')  # Redirect to the login page

@login_required(login_url="/admin-login/")
def admin_dashboard(request):
    # Total Orders
    total_orders = Order.objects.count()

    # # Total Products (You can change this if necessary)
    total_products = Product.objects.count()

    # # Total Sales
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # # Total Users
    total_users = UserProfile.objects.count()

    # # Get Sales Over Time (example: monthly sales)
    sales_over_time = Order.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=365)) \
        .values('created_at__month') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('created_at__month')

    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_users': total_users,
        'sales_over_time': sales_over_time,
    }

    return render(request, 'admin/dashboard.html',context=context)

# Manage Categories (with Pagination)
@login_required
def manage_categories(request):
    categories = ProductCategory.objects.all()
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/manage_categories.html', {'page_obj': page_obj})

# Add Category
@login_required
def product_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")  # Success message
            return redirect('manage_categories')
        else:
            messages.error(request, "Failed to add category. Please check the form.")  # Error message
    else:
        form = CategoryForm()
    return render(request, 'admin/add_category.html', {'form': form})

# Update Category
@login_required
def product_update_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")  # Success message
            return redirect('manage_categories')
        else:
            messages.error(request, "Failed to update category. Please check the form.")  # Error message
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/update_category.html', {'form': form, 'category': category})

# Delete Category
@login_required
def product_delete_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully!")  # Success message
        return redirect('manage_categories')
    return render(request, 'admin/delete_category.html', {'category': category})

# Manage Subcategories
@login_required
def product_manage_subcategories(request):
    subcategories = ProductSubcategory.objects.select_related('category').all()
    paginator = Paginator(subcategories, 10)  # Show 10 subcategories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/manage_subcategories.html', {'page_obj': page_obj})

# Add Subcategory
@login_required
def product_add_subcategory(request):
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Subcategory added successfully!")
            return redirect('manage_subcategories')
        else:
            messages.error(request, "Failed to add subcategory. Please check the form.")
    else:
        form = SubcategoryForm()
    return render(request, 'admin/add_subcategory.html', {'form': form})

# Update Subcategory
@login_required
def product_update_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(ProductSubcategory, id=subcategory_id)
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, "Subcategory updated successfully!")
            return redirect('manage_subcategories')
        else:
            messages.error(request, "Failed to update subcategory. Please check the form.")
    else:
        form = SubcategoryForm(instance=subcategory)
    return render(request, 'admin/update_subcategory.html', {'form': form, 'subcategory': subcategory})

# Delete Subcategory
@login_required
def product_delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(ProductSubcategory, id=subcategory_id)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, "Subcategory deleted successfully!")
        return redirect('manage_subcategories')
    return render(request, 'admin/delete_subcategory.html', {'subcategory': subcategory})

# Manage Products (with Pagination)
@login_required
def manage_products(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/manage_products.html', {'page_obj': page_obj})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('manage_products')
        else:
            messages.error(request, "Failed to add product. Please check the form.")
    else:
        form = ProductForm()
    return render(request, 'admin/add_product.html', {'form': form})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('manage_products')
        else:
            messages.error(request, "Failed to update product. Please check the form.")
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/update_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('manage_products')
    return render(request, 'admin/delete_product.html', {'product': product})


# Manage Discounts
def manage_discounts(request):
    discounts = Offer.objects.all()
    return render(request, 'admin/manage_discounts.html', {'discounts': discounts})

# Add Discount
def add_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount added successfully!")
            return redirect('manage_discounts')
        else:
            messages.error(request, "Error adding discount. Please check the form.")
    else:
        form = DiscountForm()
    return render(request, 'admin/add_discount.html', {'form': form})

# Update Discount
def update_discount(request, offer_id):
    discount = get_object_or_404(Offer, id=offer_id)
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount updated successfully!")
            return redirect('manage_discounts')
        else:
            messages.error(request, "Error updating discount. Please check the form.")
    else:
        form = DiscountForm(instance=discount)
    return render(request, 'admin/update_discount.html', {'form': form, 'discount': discount})

# Delete Discount
def delete_discount(request, offer_id):
    discount = get_object_or_404(Offer, id=offer_id)  # Use `id` unless you specifically use `offer_id`
    
    if request.method == 'POST':
        discount.delete()
        messages.success(request, "Discount deleted successfully!")
        return redirect('manage_discounts')
    
    return render(request, 'admin/delete_discount.html', {'discount': discount})


# Manage Orders
# def manage_orders(request):
#     orders = Order.objects.all()
#     return render(request, 'admin/manage_orders.html', {'orders': orders})
def manage_orders(request):
    orders = Order.objects.select_related('user').all()  # Optimize query
    return render(request, 'admin/manage_orders.html', {'orders': orders})

# Add Order
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Order added successfully!")
            return redirect('manage_orders')
        else:
            messages.error(request, "Error adding order. Please check the form.")
    else:
        form = OrderForm()
    return render(request, 'admin/add_order.html', {'form': form})

# Update Order
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('manage_orders')
        else:
            messages.error(request, "Error updating order. Please check the form.")
    else:
        form = OrderForm(instance=order)
    return render(request, 'admin/update_order.html', {'form': form, 'order': order})

# Delete Order
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order deleted successfully!")
        return redirect('manage_orders')
    return render(request, 'admin/delete_order.html', {'order': order})


# ----- ORDER ITEM VIEWS -----

# Manage Order Items
def manage_order_items(request):
    order_items = OrderItem.objects.all()
    return render(request, 'admin/manage_order_items.html', {'order_items': order_items})

# Delete Order Item
def delete_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if request.method == 'POST':
        order_item.delete()
        messages.success(request, "Order item deleted successfully!")
        return redirect('manage_order_items')
    return render(request, 'admin/delete_order_item.html', {'order_item': order_item})

# Manage Reviews
def manage_reviews(request):
    reviews = ProductReview.objects.all()
    return render(request, 'admin/manage_reviews.html', {'reviews': reviews})
# Delete Review+
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect('manage_reviews')
    return render(request, 'admin/delete_review.html', {'review': review})

def manage_user(request):
    # Fetch all user profiles
    user_profiles = UserProfile.objects.all()  # Or filter if needed
    print("this is a users",user_profiles)
    return render(request, 'admin/manage_user.html', {'user_profiles': user_profiles})
# Delete User
@login_required
def delete_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, id=user_id)
    if request.method == 'POST':
        user_profile.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('manage_users')  # Redirect to a user management list page (not shown here)
    return render(request, 'admin/delete_user.html', {'user_profile':user_profile})
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Ensure you have installed xhtml2pdf
# from .models import Order  # Import your Order model

def generate_report(request):
    orders = Order.objects.all()
    template_path = 'admin/report.html'  # Ensure this file exists in the templates directory
    context = {'orders': orders}
    
    template = get_template('admin/report.html' )
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    
    return response

def download_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        orders = Order.objects.filter(order_date__date__range=[start_date, end_date])
        pdf_buffer = generate_pdf(orders)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="order_report.pdf"'
        return response
    else:
        return HttpResponse("Invalid date range", status=400)
    
    
    

def add_stylist(request):
    form = StylistForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Stylist added successfully!')
            return redirect('manage_stylists')
    return render(request, 'admin/stylist_form.html', {'form': form})

# List Stylists
def manage_stylists(request):
    stylists = Stylist.objects.all()
    return render(request, 'admin/manage_stylists.html', {'stylists': stylists})

# Update Stylist
def update_stylist(request, stylist_id):
    stylist = get_object_or_404(Stylist, id=stylist_id)
    form = StylistForm(request.POST or None, instance=stylist)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Stylist updated successfully!')
        return redirect('manage_stylists')
    return render(request, 'admin/stylist_form.html', {'form': form})

# Delete Stylist
def delete_stylist(request, stylist_id):
    stylist = get_object_or_404(Stylist, id=stylist_id)
    stylist.delete()
    messages.success(request, 'Stylist deleted successfully!')
    return redirect('manage_stylists')

# List all slots
def manage_slots(request):
    slots = Slot.objects.all()
    return render(request, 'admin/slot_management.html', {'slots': slots})

# Add a new slot
def add_slot(request):
    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_slots')
    else:
        form = SlotForm()
    return render(request, 'admin/add_edit_slot.html', {'form': form})

# Update an existing slot
def update_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    if request.method == 'POST':
        form = SlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return redirect('manage_slots')
    else:
        form = SlotForm(instance=slot)
    return render(request, 'admin/add_edit_slot.html', {'form': form})

# Delete a slot
def delete_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    if request.method == 'POST':
        slot.delete()
        return redirect('manage_slots')
    return render(request, 'admin/confirm_delete.html', {'slot': slot})


# from .models import ServiceCategory, ServiceSubcategory

# Category List
def manage_service_categories(request):
    categories = ServiceCategory.objects.all().order_by('-id')
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/s_category_list.html', {'page_obj': page_obj})

def add_service_category(request):
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_service_categories')
    else:
        form = ServiceCategoryForm()
    return render(request, 'admin/s_add_edit_category.html', {'form': form, 'title': 'Add Service Category'})

def update_service_category(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('manage_service_categories')
    else:
        form = ServiceCategoryForm(instance=category)
    return render(request, 'admin/s_add_edit_category.html', {'form': form, 'title': 'Edit Service Category'})

def delete_service_category(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('manage_service_categories')

# Subcategory List
def service_subcategory_list(request):
    subcategories = ServiceSubcategory.objects.all()
    return render(request, 'admin/s_subcategory_list.html', {'subcategories': subcategories})

# Add/Edit Subcategory
# def service_add_edit_subcategory(request, subcategory_id=None):
#     subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id) if subcategory_id else None
#     categories = ServiceCategory.objects.all()

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         category_id = request.POST.get('category')
#         category = get_object_or_404(ServiceCategory, id=category_id)

#         if subcategory:
#             subcategory.name = name
#             subcategory.category = category
#             messages.success(request, "Subcategory updated successfully!")
#         else:
#             subcategory = ServiceSubcategory.objects.create(name=name, category=category)
#             messages.success(request, "Subcategory added successfully!")
#         subcategory.save()
#         return redirect('s_add_subcategory')

#     return render(request, 'admin/s_add_edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})
def service_add_edit_subcategory(request, subcategory_id=None):
    subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id) if subcategory_id else None
    categories = ServiceCategory.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        next_url = request.POST.get('next')  # This will hold the referrer URL

        category = get_object_or_404(ServiceCategory, id=category_id)

        if subcategory:
            subcategory.name = name
            subcategory.category = category
            messages.success(request, "Subcategory updated successfully!")
        else:
            subcategory = ServiceSubcategory.objects.create(name=name, category=category)
            messages.success(request, "Subcategory added successfully!")
        subcategory.save()

        # Redirect back to the previous page, or fallback to subcategory list
        return redirect(next_url or 's_subcategory_list')

    # Get the previous URL from the request headers
    previous_url = request.META.get('HTTP_REFERER', '')

    return render(request, 'admin/s_add_edit_subcategory.html', {
        'subcategory': subcategory,
        'categories': categories,
        'next': previous_url
    })


# Delete Subcategory
from django.views.decorators.http import require_POST

@require_POST
def service_delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id)
    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully!")
    return redirect('s_subcategory_list')



def service_list(request):
    services = Service.objects.all()
    return render(request, 'admin/service_list.html', {'services': services})

def add_edit_service(request, service_id=None):
    if service_id:
        service = get_object_or_404(Service, id=service_id)
    else:
        service = None

    subcategories = ServiceSubcategory.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        subcategory_id = request.POST.get('subcategory')
        subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id)

        if service:
            service.name = name
            service.subcategory = subcategory
            service.save()
        else:
            Service.objects.create(name=name, subcategory=subcategory)

        return redirect('service-list')

    return render(request, 'admin/service_form.html', {'service': service, 'subcategories': subcategories})

from django.views.decorators.http import require_POST

@require_POST
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    return redirect('service-list')


from django.shortcuts import render, get_object_or_404, redirect
# from home.models import Appointment
from adminpanel.forms import AppointmentForm

# List all appointments
def appointment_list(request):
    appointments = Appointment.objects.all()
    return render(request, 'admin/appointment_list.html', {'appointments': appointments})

# Add a new appointment
def appointment_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'admin/appointment_form.html', {'form': form})

# Edit an existing appointment
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'admin/appointment_form.html', {'form': form})

# Delete an appointment
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'admin/appointment_confirm_delete.html', {'appointment': appointment})
