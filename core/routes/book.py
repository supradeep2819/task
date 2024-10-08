import json
from django.utils import timezone
from typing import List
from ninja import Router
from pydantic import Json

from core.models import Book, Lend, Role, Status
from core.schemas import BookSchema, BookSchemaIn, DetailSchema, LendSchema
from django.core.exceptions import PermissionDenied
from django.db import transaction

from core.routes.librarian import check_librarian_role

router = Router()

@router.post('/books/add/',response={200: BookSchema, 400: DetailSchema})
def add_book(request,payload:BookSchemaIn):
    data = payload.dict()
    try:
        check_librarian_role(request)
        if data['price'] <0:
            raise ValueError("Price cannot be negative")
        if data['status'] not in   [Status.AVAILABLE.value, Status.BORROWED.value]:
            raise ValueError("Book status can only be 'AVAILABLE' or 'BORROWED'.")
        book = Book.objects.create(**data)
        return book      
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.get('/books/',response={200: List[BookSchema], 400: DetailSchema})
def get_books(request):
    try:
        books = Book.objects.all()
        return books    
    except Exception as e:
        return 400, {"detail": str(e)}
    


@router.get('/books/{book_id}/', response={200: BookSchema, 400: DetailSchema})
def get_book_by_id(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        return book
    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
    
@router.delete('/books/{book_id}/', response={200: Json, 400: DetailSchema})
def delete_book(request, book_id):
    try:
        check_librarian_role(request)
        lend = Lend.objects.filter(book=book,returned_at=None).first()
        if lend:
            raise Exception("Book is currently borrowed. You can't delete it until it's returned.")
        book = Book.objects.get(id=book_id)
        book.delete()
        return {"detail": "Book deleted successfully"}
    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
    
@router.put('/books/{book_id}/', response={200: BookSchema, 400: DetailSchema})
def update_book(request, book_id, payload: BookSchemaIn):
    try:
        
        check_librarian_role(request)
        
        lend = Lend.objects.filter(book=book,returned_at=None).first()
        if lend:
            raise Exception("Book is currently borrowed. You can't update it until it's returned.")

        # Fetch the book
        book = Book.objects.get(id=book_id)
        data = payload.dict()

        # Check if the status is valid
        if 'status' in data and data['status'] not in [Status.AVAILABLE.value, Status.BORROWED.value]:
            raise Exception("Book status can only be 'AVAILABLE' or 'BORROWED'.")

        # Update the book attributes
        for key, value in data.items():
            setattr(book, key, value)

        # Save the book instance
        book.save()
        return book

    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.post('/books/{book_id}/lend/', response={200: LendSchema, 400: DetailSchema})
def lend_book(request, book_id):
    try:
        # Fetch the book
        book = Book.objects.get(id=book_id)
        # Check if the book is available
        if book.status == Status.BORROWED.value:
            raise Exception("Book is already borrowed")
        # Update the book status
        book.status = Status.BORROWED.value
        book.save()
        # Create a new lend instance
        lend = Lend.objects.create(book=book, user=request.user)
        return lend
    except Exception as e:
        return 400, {"detail": str(e)}


@router.post('/books/{book_id}/return/', response={200: Json, 400: DetailSchema})
def return_book(request, book_id):
    try:
        with transaction.atomic():
            # Fetch the book
            book = Book.objects.get(id=book_id)
            # Check if the book is borrowed
            if book.status == Status.AVAILABLE.value:
                raise Exception("Book is not borrowed")
            # Update the book status
            book.status = Status.AVAILABLE.value
            book.save()
            # Update the lend instance
            lend = Lend.objects.filter(book=book,returned_at=None).first()
            if lend:
                lend.returned_at = timezone.now()
                lend.save()
            return json.dumps({"detail": "Book returned successfully"})
    except Exception as e:
        return 400, {"detail": str(e)}