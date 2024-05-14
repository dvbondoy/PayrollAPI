from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import oauth2, utils, oauth2
from ..dbase import cursor


router = APIRouter(
    tags=["Auth"]
)

@router.post("/login")
def login(cred: OAuth2PasswordRequestForm = Depends()):#, db: Session = Depends(database.get_db)):

    cursor.execute("SELECT * FROM employee WHERE id_number = %s", (cred.username,))
    employee = cursor.fetchone()
    # employee = db.query(models.Employees).filter(models.Employees.id_number == cred.username).first()
    # user = db.query(models.Users).filter(models.Users.username == cred.username).first()
    
    if not employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    if not utils.verify(cred.password, employee.get('password')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    access_token = oauth2.create_access_token(data = {"employee_id": employee.get('id')})

    return {"access_token": access_token, "token_type": "bearer"}
