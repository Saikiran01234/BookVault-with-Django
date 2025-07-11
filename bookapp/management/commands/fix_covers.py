import os
import re
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from bookapp.models import Book

class Command(BaseCommand):
    help = 'Download book cover images from URLs and update Book.cover_image to use local files.'

    def add_arguments(self, parser):
        parser.add_argument('--fix-blue-umbrella', action='store_true', help='Force update The Blue Umbrella cover to the correct local file.')
        parser.add_argument('--fix-charlie', action='store_true', help='Force update Charlie and the Chocolate Factory cover to the correct local file.')

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        covers_dir = os.path.join(media_root, 'covers')
        os.makedirs(covers_dir, exist_ok=True)

        if options.get('fix_blue_umbrella'):
            # Force update The Blue Umbrella cover
            book = Book.objects.filter(title__iexact='The Blue Umbrella').first()
            if book:
                book.cover_image = 'covers/the_blue_umbrella.jpg'
                book.save()
                self.stdout.write(self.style.SUCCESS("Updated 'The Blue Umbrella' cover to the correct local file."))
            else:
                self.stderr.write("Could not find 'The Blue Umbrella' in the database.")
            return

        if options.get('fix_charlie'):
            # Force update Charlie and the Chocolate Factory cover
            book = Book.objects.filter(title__icontains='Charlie and the Chocolate Factory').first()
            if book:
                book.cover_image = 'covers/charlie_and_the_chocolate_factory.jpg'
                book.save()
                self.stdout.write(self.style.SUCCESS("Updated 'Charlie and the Chocolate Factory' cover to the correct local file."))
            else:
                self.stderr.write("Could not find 'Charlie and the Chocolate Factory' in the database.")
            return

        books = Book.objects.all()
        updated = 0
        for book in books:
            cover_str = str(book.cover_image)
            if not cover_str.startswith('http'):
                continue
            url = cover_str
            # Clean filename
            safe_title = re.sub(r'[^a-zA-Z0-9]+', '_', book.title.lower())
            ext = os.path.splitext(url)[1]
            if not ext or len(ext) > 5:
                ext = '.jpg'
            filename = f"{safe_title}{ext}"
            local_path = os.path.join('covers', filename)
            full_path = os.path.join(media_root, local_path)
            
            if not os.path.exists(full_path):
                self.stdout.write(f"Downloading {book.title} cover...")
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                except Exception as e:
                    self.stderr.write(f"Failed to download {url}: {e}")
                    continue
            else:
                self.stdout.write(f"Cover already exists for {book.title}")
            # Update model
            book.cover_image = local_path
            book.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} book covers.")) 