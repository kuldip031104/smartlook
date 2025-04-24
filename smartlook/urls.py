"""
URL configuration for smartlook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
import adminpanel.views 

urlpatterns = [
    path('',views.home,name='home'),
    # path('admin/', admin.site.urls),
    path('adminhome/',include('adminpanel.urls')),
    path('admin-login/', adminpanel.views.admin_login, name='admin_login'),
    path('about/',views.about,name='about'),
    path('services/',views.services,name='services'),
    path('male/',views.male,name='male'),
    path('female/',views.female,name='female'),
    path('services-details/',views.servicesdetails,name='servicesdetails'),
    # path('team/',views.team,name='team'),
    # path('team/', views.team_list_user, name='user_team_list'),

    # path('cart/',views.cart,name='cart'),
    # path('checkout/',views.checkout,name='checkout'),
    path('contact/',views.contact,name='contact'),
    # path('contactus1',views.contactus1,name="contactus1"),
    path('product-page/',views.product,name='productpage'),
    # path('team/',views.team,name='team'),
    # path('appointment/',views.BookAppointmentView,name='appointment'),
    path('gallery/',views.gallery,name='gallery'),
    path('productcategory/', views.product_category, name="productcategory"),
    path('category/<str:category_name>/', views.product_sub_category, name="subcategory"),
    path('product/<str:subcategory_name>/', views.product, name="product"),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('manageprofile/',views.manageprofile,name='manageprofile'),
    path('editprofile/', views.edit_prof, name='edit_profile'),
    path('logout/',views.logout,name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:cart_id>/<str:action>/', views.update_cart, name='update_cart'),
    

    path("cart/", views.cart, name="cart"), 
    path('delete_cart_item/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('delete_all_cart_items/', views.delete_all_cart_items, name='delete_all_cart_items'),

    
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),  # Add this line
    
    path('servicecategory/', views.service_category, name="servicecategory"),
    path('servicesubcategory/<str:category_name>/', views.service_sub_category, name="service_sub_category"),
    path('services/<str:subcategory_name>/', views.services, name="services"),
    
    path('stylists/', views.StylistListView.as_view(), name='stylist-list'),
    path('slots/<int:stylist_id>/<str:date>/', views.AvailableSlotsView.as_view(), name='available-slots'),
    path('service-subcategories/<int:category_id>/', views.get_filtered_subcategories, name='filtered-service-subcategories'),
    path('book-appointment/', views.book_appointment, name='appointment'),
     path('payment-success/', views.payment_success, name='payment_success'),
    path('product/details/<int:product_id>/', views.product_detail, name='product_detail'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
