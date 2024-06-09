from fastapi import Depends, HTTPException, status, APIRouter
from app import schemas, oauth2, utils
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/payroll_perk",
    tags=["Payroll Perk"]
)

# retrieve payrolls by payroll_id
@router.get("/{id}")
def get_payroll_perk(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM pay_perk WHERE payroll_id = %s", (id,))
    payroll_perk = cursor.fetchall()
    if not payroll_perk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payroll Perk not found")
    
    return payroll_perk
