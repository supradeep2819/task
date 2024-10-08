import json
from typing import List
from ninja import Router
from pydantic import Json

from core.schemas import DetailSchema, LendSchema
from core.models import Lend


router = Router()

@router.delete('/user/delete/',response={200: Json, 400: DetailSchema})
def delete_user(request):
    try:
        user = request.user
        lend = Lend.objects.filter(user=user, returned_at=None).first()
    
        if lend:
            raise Exception("You can't delete your account while you have a book borrowed.")
        request.user.is_active = False
        request.user.save()
        return json.dumps({"detail": "User deleted successfully"})
    except Exception as e:
        return 400, {"detail": str(e)}
    
@router.get('/user/lend/history/',response={200: List[LendSchema], 400: DetailSchema})
def get_lend_history(request):
    try:
        user = request.user
        lends = Lend.objects.filter(user=user)
        return lends
    except Exception as e:
        return 400, {"detail": str(e)}