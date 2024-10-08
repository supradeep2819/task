import json
from typing import List
from ninja import Router
from pydantic import Json

from core.schemas import DetailSchema, LendSchema, UserSchemaOut
from core.models import Lend, Role, User


router = Router()

def check_librarian_role(request)->bool:
    if request.user.role != Role.LIBRARIAN.value:
        raise Exception("Only librarians can access this route")
    else :
        return True

@router.delete('/users/{member_id}/remove/',response={200: Json, 400: DetailSchema})
def remove_member(request, user_id):
    try:
        #check for librarian role
        check_librarian_role(request)
        # Check if the member exists
        if not User.objects.filter(id=user_id).exists():
            raise Exception("Member not found")
        # Fetch the member
        user = User.objects.get(id=user_id)
        lend = Lend.objects.filter(user=user, returned_at=None).first()
        if lend:
            raise Exception("Member is currently borrowing a book. You can't remove them until it's returned.")
        # Delete the member
        user.is_active = False
        return json.dumps({"detail": "Member removed successfully"})
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.get('/users/history/',response={200: List[LendSchema], 400: DetailSchema})
def get_users_lend_history(request):
    try:
        #check for librarian role
        check_librarian_role(request)
        # Fetch the member
        lends = Lend.objects.all()
        return lends
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.get('/users/active/',response={200: List[UserSchemaOut], 400: DetailSchema})
def get_active_members(request):
    try:
        check_librarian_role(request)
        users = User.objects.filter(active=True)
        return users
    except Exception as e:
        return 400, {"detail": str(e)} 
    
@router.get('/users/inactive/',response={200: List[UserSchemaOut], 400: DetailSchema})
def get_inactive_members(request):
    try:
        check_librarian_role(request)
        users = User.objects.filter(active=False)
        return users
    except Exception as e:
        return 400, {"detail": str(e)}