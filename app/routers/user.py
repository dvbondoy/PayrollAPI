from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    print(current_user.id)
    user = db.query(models.Users).all()
    return user

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    # new_account = models.Users(username=account.username, password=account.password)
    new_user = models.Users(**user.model_dump())

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        # print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    return new_user

@router.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    return user

@router.put("/{id}")
def update_user(id: int, user: schemas.User, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # db.query(models.Users).filter(models.Users.id == id).update({"username": user.username, "password": user.password})
    user.password = utils.hash(user.password)
    db.query(models.Users).filter(models.Users.id == id).update(user.model_dump())

    try:
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    return {"data": f"User with id {id} has been updated"}

@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.delete(synchronize_session=False)
    db.commit()
   
    return Response(status_code=status.HTTP_204_NO_CONTENT)