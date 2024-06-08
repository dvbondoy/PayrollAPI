from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2, utils
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/overtime",
    tags=["Overtime"]
)

@router.get("/")
def get_overtimes(current_user: dict = Depends(oauth2.get_current_user)):   
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM overtime")
    overtimes = cursor.fetchall()
    return overtimes


@router.get("/{id}")
def get_overtime(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM overtime WHERE id = %s", (str(id),))
    overtime = cursor.fetchone()
    if not overtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Overtime not found")
    return overtime

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_overtime(overtime: schemas.Overtime, current_user: dict = Depends(oauth2.get_current_user)):
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])

    #retrieve attendance of employee_id
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND end_date BETWEEN %s AND %s", (str(overtime.employee_id),overtime.start_date,overtime.end_date))
    
    cursor.execute("""INSERT INTO overtime (employee_id, supervisor_id, start_date, end_date, total_hours, approved) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""", 
                   (overtime.employee_id, overtime.supervisor_id, overtime.start_date, overtime.end_date, overtime.total_hours, overtime.approved))
    new_overtime = cursor.fetchone()
    conn.commit()

    return new_overtime