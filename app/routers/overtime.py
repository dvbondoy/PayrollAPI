from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2, utils
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/overtime",
    tags=["Overtime"]
)

@router.get("/")
def get_overtimes(current_user: dict = Depends(oauth2.get_current_user)) -> list[schemas.OvertimeResponse]:   
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin','user'])
    
    cursor.execute("SELECT * FROM overtime")
    overtimes = cursor.fetchall()
    return overtimes