import json
from fastapi.responses import JSONResponse
from ninja import Router, NinjaAPI
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from pydantic import Json
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response
from rest_framework import status
from core.models import Role, User
from core.schemas import DetailSchema, LogInSchema, RegisterInSchema, UserSchemaOut
import logging
from fastapi import APIRouter, HTTPException
from core.routes.book import router as book_router
from core.routes.librarian import router as librarian_router
from core.routes.user import router as user_router
logger = logging.getLogger(__name__)

# User model
User = get_user_model()

# Ninja API instance
api = NinjaAPI(
    version="1.0",
    csrf=False,
    title="Valmi App Backend API",
    description="App Backend API Serves the Valmi App Frontend",
)

# Public Router for routes accessible without authentication
public_router = Router() 

@public_router.post("/register/", response={200: dict, 400: DetailSchema})
def register(request, register_schema: RegisterInSchema):
    req = register_schema.dict()
    try:
        if User.objects.filter(username=req["username"]).exists():
            raise Exception("Username already exists")

        user = User(
            username=req["username"], 
            email=req["email"], 
            password=make_password(req["password"])
        )
        user.role = req.get("role") or Role.MEMBER.value
        if user.role not in [Role.LIBRARIAN.value, Role.MEMBER.value]:
            raise Exception(f"Invalid role: {user.role}. Role must be either 'librarian' or 'member'.")
        print(f"Assigning role: {user.role}")
        print(user)
        user.save()
        
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        response = {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }
        return response
    except Exception as e:
        return 400, {"detail": str(e)}



# Login Route - Anyone can access
@public_router.post("/login/", response={200: dict, 400: DetailSchema})
def login(request, login_req: LogInSchema):  # Add the request parameter
    req = login_req.dict()

    try:
        user = User.objects.filter(username=req["username"]).first()
        if user and user.check_password(req["password"]):
            if not user.is_active:
                raise Exception("User is inactive. Please contact the admin.")
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            response = {
                'access_token': str(access_token),  # Corrected key name
                'refresh_token': str(refresh_token),  # Ensure token is string
            }
            return response  # Return the response directly
        else:
            raise Exception("Invalid username or password")
    except Exception as e:
        return 400, {"detail": str(e)}


### AUTHENTICATED/PROTECTED ROUTES ###

class AuthBearer:
    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        token_type, token = auth_header.split()
        if token_type.lower() != 'bearer':
            return None
        try:
            # Validate the token
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            if not user.is_active:
                raise Exception("User is inactive and cannot access this route.")
            request.user = user  # Attach user to request
            return token
        except Exception:
            return None



# Add Public and Protected Routers to the Main API
api.add_router("/v1/auth", public_router)
protected_router = Router(auth=[AuthBearer()])
protected_router.add_router("",book_router)
protected_router.add_router("",librarian_router)
protected_router.add_router("",user_router)
api.add_router("v1/", protected_router)
