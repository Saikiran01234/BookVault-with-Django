from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings

class Book(models.Model):
    GENRE_CHOICES = [
        ("fiction", "Fiction"),
        ("mystery", "Mystery"),
        ("fantasy", "Fantasy"),
        ("science", "Science"),
        ("biography", "Biography"),
        ("romance", "Romance"),
        ("history", "History"),
        ("selfhelp", "Self-Help"),
        ("children", "Children"),
        ("other", "Other"),
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    ebook_file = models.FileField(upload_to='ebooks/')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Price in INR")
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default="other")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    class Meta:
        ordering = ['-uploaded_at']

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    discount_percent = models.PositiveIntegerField(default=10, help_text="Discount percent (10-25%)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        discount_multiplier = Decimal('1') - (Decimal(self.discount_percent) / Decimal('100'))
        discounted_price = self.book.price * discount_multiplier
        return discounted_price * self.quantity

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    books = models.ManyToManyField(Book, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReadBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} read {self.book.title}"
