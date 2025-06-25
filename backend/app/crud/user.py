from sqlalchemy.orm import Session

from .. import models, schemas
from ..utils.hashing import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = hash_password(user.password)
    db_user = models.User(
        name=user.name, email=user.email, hashed_password=hashed_pwd, role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(
    db: Session, updating_user: models.User, user_update=schemas.UserUpdate
):
    for key, value in user_update.model_dump().items():
        setattr(updating_user, key, value)

    db.commit()
    db.refresh(updating_user)
    return updating_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
