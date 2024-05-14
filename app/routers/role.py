from .. import schemas, models, oauth2
from .. import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    include_in_schema=False
)

@router.get("/")#, response_model=list[schemas.RoleResponse])
def get_roles(db: Session = Depends(database.get_db),current_user: int = Depends(oauth2.get_current_user),limit:int=10):# -> list[schemas.RoleResponse]:
    roles = db.query(models.Roles).all()

    #test join in sqlalchemy
    #should create a response model for this
    results = db.query(
        models.Roles, func.count(models.Employees.id).label("total")).join(
            models.Employees, models.Employees.id == models.Roles.employee_id, isouter=True).group_by(
                models.Roles.id).filter().limit(limit).all()
    
    resultd = db.query(models.Roles).join(models.Employees, models.Employees.id == models.Roles.employee_id, isouter=True)
    resulta = db.query(models.Employees.id, func.count(models.Roles.employee_id)).join(models.Roles, models.Roles.employee_id == models.Employees.id, isouter=True).group_by(models.Employees.id)
    resultb = db.query(func.count(models.Employees.id).label("total"))
    # does not work
    result = db.query(models.Employees, func.count(models.Roles.employee_id).label("total")).select_from(models.Employees).join(models.Roles, models.Roles.employee_id == models.Employees.id, isouter=True)
    resultc = db.query(func.count(models.Employees.id).label("total"))
    print(resultc)


    # return roles
    return resultc.scalar()

@router.get("/search", response_model=List[schemas.RoleResponse])
def search_roles(db: Session = Depends(database.get_db),current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    roles = db.query(models.Roles).filter(models.Roles.role.contains(search)).limit(limit).offset(skip).all()
    return roles

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_role(role: schemas.Role, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user)

    check_role = db.query(models.Roles).filter(models.Roles.role == role.role and models.Roles.employee_id == current_user.id).first()

    if check_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    else:
        new_role = models.Roles(employee_id=current_user.id, **role.model_dump())

        try:
            db.add(new_role)
            db.commit()
            db.refresh(new_role)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    
    return new_role

@router.delete("/{id}")
def delete_role(id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    role = db.query(models.Roles).filter(models.Roles.id == id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    try:
        db.delete(role)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role cannot be deleted")
    
    return {"data": f"Role with id {id} has been deleted"}