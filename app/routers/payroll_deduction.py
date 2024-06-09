from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2, utils
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/payroll_deduction",
    tags=["Payroll Deduction"]
)

# retrieve payrolls by payroll_id
@router.get("/{id}")
def get_payroll_deduction(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM pay_deduction WHERE payroll_id = %s", (id,))
    payroll_deduction = cursor.fetchall()
    if not payroll_deduction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payroll Deduction not found")
    
    return payroll_deduction