from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user import user as user_repo
from app.schemas.user import UserUpdate, PasswordUpdate
from app.models import User
from app.core.security import verify_password, get_password_hash

class UserService:
    def update_profile(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        return user_repo.update(db, db_obj=db_obj, obj_in=obj_in)

    def change_password(self, db: Session, *, db_obj: User, obj_in: PasswordUpdate) -> User:
        if not verify_password(obj_in.current_password, db_obj.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password",
            )
        new_password_hash = get_password_hash(obj_in.new_password)
        return user_repo.update(db, db_obj=db_obj, obj_in={"password_hash": new_password_hash})

user_service = UserService()
