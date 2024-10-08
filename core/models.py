import uuid
from django.db import models
from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(Enum):
    LIBRARIAN = "librarian"
    MEMBER = "member"

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20, 
        choices=[(role.value, role.name) for role in Role],
        default=Role.MEMBER.value
    )

class Status(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[(status.value, status.name) for status in Status], default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Lend(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lend_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)