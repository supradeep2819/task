from typing import Optional
from ninja import ModelSchema, Schema

from core.models import Book, Lend


def camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


class CamelSchemaConfig(Schema.Config):
    alias_generator = camel_to_snake
    allow_population_by_field_name = True

class UserSchemaOut(Schema):
    username: str
    email: str
    role: str

class LogInSchema(Schema):
    username:str
    password:str

class DetailSchema(Schema):
    detail: str


class RegisterInSchema(Schema):
    username: str
    email: str
    password: str
    role: Optional[str] = None


class BookSchema(ModelSchema):
    class Config(CamelSchemaConfig):
        model = Book
        model_fields = ["id","title","author","price","status","created_at","updated_at"]


class BookSchemaIn(Schema):
    title: str
    author: str
    price: float
    status: str

class LendSchema(ModelSchema):
    class Config(CamelSchemaConfig):
        model = Lend
        model_fields = ["id","user","book","lend_at","returned_at"]
    
class UserSchemaOut(Schema):
    username: str
    email: str
    role: str