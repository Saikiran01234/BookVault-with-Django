from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .models import Book, Cart, CartItem, Wishlist, ReadBook
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random
from django.urls import reverse
from django.db import models
from itertools import chain

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to BookVault.')
            return redirect('bookapp:home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('bookapp:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('bookapp:home')

def home_view(request):
    return render(request, 'home.html')

def browse_books_view(request):
    genre = request.GET.get('genre')
    search_query = request.GET.get('q', '').strip()
    books = Book.objects.all()
    if genre:
        books = books.filter(genre=genre)
    searched = False
    if search_query:
        books = books.filter(models.Q(title__icontains=search_query) | models.Q(author__icontains=search_query))
        searched = True
    cart_book_ids = set()
    read_book_ids = set()
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_book_ids = set(cart.items.values_list('book_id', flat=True))
        read_book_ids = set(ReadBook.objects.filter(user=request.user).values_list('book_id', flat=True))
    return render(request, 'browse_books.html', {
        'books': books,
        'selected_genre': genre,
        'cart_book_ids': cart_book_ids,
        'read_book_ids': read_book_ids,
        'search_query': search_query,
        'searched': searched,
    })

def user_profile_view(request):
    cart_items = []
    wishlist_books = []
    cart_total = 0
    read_books = []
    user_info = {}
    stats = {}
    recent_activity = []
    if request.user.is_authenticated:
        user = request.user
        user_info = {
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        }
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_items = cart.items.select_related('book').all()
        cart_total = sum(i.get_total_price() for i in cart_items)
        wishlist, _ = Wishlist.objects.get_or_create(user=user)
        wishlist_books = wishlist.books.all()
        read_books = Book.objects.filter(readbook__user=user)
        # Stats
        stats = {
            'read_count': read_books.count(),
            'cart_count': cart_items.count(),
            'wishlist_count': wishlist_books.count(),
            'most_read_genre': read_books.values('genre').annotate(count=models.Count('id')).order_by('-count').first(),
        }
        # Recent activity: last 5 actions (cart, wishlist, read)
        cart_acts = [{'type': 'cart', 'book': i.book, 'date': i.created_at} for i in cart_items.order_by('-created_at')[:5]]
        wish_acts = [{'type': 'wishlist', 'book': b, 'date': user.date_joined} for b in wishlist_books.order_by('-id')[:5]]
        read_acts = [{'type': 'read', 'book': b, 'date': b.readbook_set.get(user=user).marked_at} for b in read_books.order_by('-readbook__marked_at')[:5]]
        recent_activity = sorted(chain(cart_acts, wish_acts, read_acts), key=lambda x: x['date'], reverse=True)[:5]
    return render(request, 'user_profile.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'wishlist_books': wishlist_books,
        'read_books': read_books,
        'user_info': user_info,
        'stats': stats,
        'recent_activity': recent_activity,
    })

@require_POST
@login_required
def add_to_cart(request):
    book_id = request.POST.get('book_id')
    if not book_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No book_id provided.'}, status=400)
        else:
            messages.error(request, 'No book_id provided.')
            return redirect('bookapp:browse_books')
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Book not found.'}, status=404)
        else:
            messages.error(request, 'Book not found.')
            return redirect('bookapp:browse_books')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if created:
        item.discount_percent = random.randint(10, 25)
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()
    # Calculate new cart total
    total = sum(i.get_total_price() for i in cart.items.all())
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(total),
            'discount_percent': item.discount_percent,
            'quantity': item.quantity,
            'book_id': book_id,
        })
    else:
        return redirect('bookapp:cart')

@require_POST
@login_required
def add_to_wishlist(request):
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'success': False, 'error': 'No book_id provided.'}, status=400)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found.'}, status=404)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.books.add(book)
    return JsonResponse({'success': True, 'book_id': book_id})

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book').all()
    total = sum(i.get_total_price() for i in items)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total': total})

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    books = wishlist.books.all()
    return render(request, 'wishlist.html', {'wishlist': wishlist, 'books': books})

@require_POST
@login_required
def remove_from_cart(request):
    book_id = request.POST.get('book_id')
    cart = get_object_or_404(Cart, user=request.user)
    item = cart.items.filter(book_id=book_id).first()
    if item:
        item.delete()
    # Recalculate total
    total = sum(i.get_total_price() for i in cart.items.all())
    return JsonResponse({'success': True, 'cart_total': float(total)})

@require_POST
@login_required
def remove_from_wishlist(request):
    book_id = request.POST.get('book_id')
    wishlist = get_object_or_404(Wishlist, user=request.user)
    book = wishlist.books.filter(id=book_id).first()
    if book:
        wishlist.books.remove(book)
    return JsonResponse({'success': True})

@require_POST
@login_required
def move_to_cart(request):
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'success': False, 'error': 'No book_id provided.'}, status=400)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found.'}, status=404)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.books.remove(book)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if created:
        item.discount_percent = random.randint(10, 25)
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()
    total = sum(i.get_total_price() for i in cart.items.all())
    return JsonResponse({'success': True, 'cart_total': float(total), 'book_id': book_id, 'quantity': item.quantity, 'discount_percent': item.discount_percent})

@require_POST
@login_required
def mark_as_read(request):
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'success': False, 'error': 'No book_id provided.'}, status=400)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Book not found.'}, status=404)
    obj, created = ReadBook.objects.get_or_create(user=request.user, book=book)
    return JsonResponse({'success': True, 'already_read': not created})

@require_POST
@login_required
def update_cart_quantity(request):
    book_id = request.POST.get('book_id')
    action = request.POST.get('action')  # 'inc' or 'dec'
    cart = get_object_or_404(Cart, user=request.user)
    item = cart.items.filter(book_id=book_id).first()
    if not item:
        return JsonResponse({'success': False, 'error': 'Item not found.'}, status=404)
    if action == 'inc':
        item.quantity += 1
        item.save()
    elif action == 'dec':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
            return JsonResponse({'success': True, 'removed': True})
    total = sum(i.get_total_price() for i in cart.items.all())
    return JsonResponse({'success': True, 'quantity': item.quantity, 'item_total': float(item.get_total_price()), 'cart_total': float(total)})

@require_POST
@login_required
def remove_from_cart_profile(request):
    book_id = request.POST.get('book_id')
    cart = get_object_or_404(Cart, user=request.user)
    item = cart.items.filter(book_id=book_id).first()
    if item:
        item.delete()
    total = sum(i.get_total_price() for i in cart.items.all())
    return JsonResponse({'success': True, 'cart_total': float(total)})
