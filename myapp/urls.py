from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/', views.product, name='product'),
    path('listproduct/', views.listproduct, name='listproduct'),
    path('quantity-plus/<int:id>/', views.increase_quantity, name='quantity_plus'),
    path('quantity-minus/<int:id>/', views.decrease_quantity, name='quantity_minus'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('edit/<int:id>/', views.edit, name='edit'),

    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('register/', views.register, name='register'),
    
    path('addcart/<int:id>/', views.addcart, name='addcart'),
    path('mycart/', views.mycart, name='mycart'),

    path('cart_quantity_pluss/<int:id>/', views.cart_quantity_pluss, name='cart_quantity_pluss'),
    path('cart_quantity_minuss/<int:id>/', views.cart_quantity_minuss, name='cart_quantity_minuss'),


    path('checkout/', views.checkout, name='checkout'),

    path('order-success/<int:id>/',views.order_success,name='order_success'),

]
