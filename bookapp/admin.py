from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_at', 'updated_at')
    list_filter = ('uploaded_at', 'author')
    search_fields = ('title', 'author', 'description')
    readonly_fields = ('uploaded_at', 'updated_at')
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'description')
        }),
        ('Files', {
            'fields': ('cover_image', 'ebook_file')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
