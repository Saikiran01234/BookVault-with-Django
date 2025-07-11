from django.urls import path
from . import views

app_name = 'bookapp'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('browse/', views.browse_books_view, name='browse_books'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('move_to_cart/', views.move_to_cart, name='move_to_cart'),
    path('mark_as_read/', views.mark_as_read, name='mark_as_read'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove_from_cart_profile/', views.remove_from_cart_profile, name='remove_from_cart_profile'),
] 