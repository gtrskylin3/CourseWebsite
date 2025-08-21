from app.utils.current_user import get_current_user
from fastapi import Depends, HTTPException, status

def is_admin(
    user = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have admin permissions")
