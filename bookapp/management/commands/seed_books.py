from django.core.management.base import BaseCommand
from bookapp.models import Book

BOOKS = [
    {
        "title": "The God of Small Things",
        "author": "Arundhati Roy",
        "price": 399,
        "genre": "fiction",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81OthjkJBuL.jpg",
    },
    {
        "title": "Midnight's Children",
        "author": "Salman Rushdie",
        "price": 499,
        "genre": "fiction",
        "cover_image": "https://m.media-amazon.com/images/I/81pQwQlmAXL.jpg",
    },
    {
        "title": "The White Tiger",
        "author": "Aravind Adiga",
        "price": 299,
        "genre": "fiction",
        "cover_image": "https://m.media-amazon.com/images/I/71Q1Iu4suSL.jpg",
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "price": 350,
        "genre": "fiction",
        "cover_image": "https://m.media-amazon.com/images/I/71aFt4+OTOL.jpg",
    },
    {
        "title": "The Guide",
        "author": "R.K. Narayan",
        "price": 299,
        "genre": "fiction",
        "cover_image": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1386924361l/129877.jpg",
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "price": 599,
        "genre": "fantasy",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81iqZ2HHD-L.jpg",
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "price": 499,
        "genre": "fantasy",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/91b0C2YNSrL.jpg",
    },
    {
        "title": "A Game of Thrones",
        "author": "George R.R. Martin",
        "price": 699,
        "genre": "fantasy",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/91dSMhdIzTL.jpg",
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "price": 499,
        "genre": "science",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81t2CVWEsUL.jpg",
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "price": 599,
        "genre": "science",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/713jIoMO3UL.jpg",
    },
    {
        "title": "Wings of Fire",
        "author": "A.P.J. Abdul Kalam",
        "price": 299,
        "genre": "biography",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81drfTT9ZfL.jpg",
    },
    {
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "price": 799,
        "genre": "biography",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81VStYnDGrL.jpg",
    },
    {
        "title": "2 States",
        "author": "Chetan Bhagat",
        "price": 250,
        "genre": "romance",
        "cover_image": "https://m.media-amazon.com/images/I/81A-mvlo+QL.jpg",
    },
    {
        "title": "The Fault in Our Stars",
        "author": "John Green",
        "price": 399,
        "genre": "romance",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81af+MCATTL.jpg",
    },
    {
        "title": "India After Gandhi",
        "author": "Ramachandra Guha",
        "price": 999,
        "genre": "history",
        "cover_image": "https://m.media-amazon.com/images/I/81dQwQlmAXL.jpg",
    },
    {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "price": 499,
        "genre": "selfhelp",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/71g2ednj0JL.jpg",
    },
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "price": 599,
        "genre": "selfhelp",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/91bYsX41DVL.jpg",
    },
    {
        "title": "The Blue Umbrella",
        "author": "Ruskin Bond",
        "price": 199,
        "genre": "children",
        "cover_image": "https://mir-s3-cdn-cf.behance.net/project_modules/hd_webp/8e43ae8014113.560b5c650a868.jpg",
    },
    {
        "title": "Charlie and the Chocolate Factory",
        "author": "Roald Dahl",
        "price": 299,
        "genre": "children",
        "cover_image": "https://images-na.ssl-images-amazon.com/images/I/81eA5wT1wUL.jpg",
    },
]

class Command(BaseCommand):
    help = 'Seed the database with real books.'

    def handle(self, *args, **kwargs):
        created = 0
        for data in BOOKS:
            book, was_created = Book.objects.get_or_create(
                title=data["title"],
                author=data["author"],
                defaults={
                    "price": data["price"],
                    "genre": data["genre"],
                    "cover_image": data["cover_image"],
                    "description": "",
                    "ebook_file": "",
                }
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} books.")) 