import calendar
from datetime import datetime
from .. import schemas, oauth2, utils
from fastapi import Depends, HTTPException, status, APIRouter
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# get all attendance
@router.get("/")
def get_attendance(current_user:int = Depends(oauth2.get_current_user), limit: int = 50, skip: int = 0):
    oauth2.check_permissions(current_user, ['hr','admin'])
    cursor.execute("SELECT * FROM attendance limit %s offset %s", (limit, skip))
    attendance = cursor.fetchall()
    return attendance

# get attendance by id
@router.get("/{id}")
def get_attendance_by_current_user(id: int, current_user: int = Depends(oauth2.get_current_user), limit: int = 50, skip: int = 0, start_date: str=datetime.date(datetime.today()).replace(day=1), 
                     end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND end_date BETWEEN %s AND %s", (str(id),start_date,end_date))
    attendance = cursor.fetchall()
    if not attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
    return attendance

# clock in current user
@router.post("/timein")
def time_in(current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND DATE(start_date) = CURRENT_DATE", (str(current_user.get('id'))))
    attendance = cursor.fetchone()
    print(attendance)

    if attendance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already timed in")
    
    cursor.execute("INSERT INTO attendance (employee_id, start_date) VALUES (%s, CURRENT_TIMESTAMP) RETURNING *", (str(current_user.get('id')),))
    new_attendance = cursor.fetchone()
    conn.commit()

    return new_attendance

# clock out current user
@router.post("/timeout")
def time_out(current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND DATE(start_date) = CURRENT_DATE;", (str(current_user.get('id')),))
    attendance = cursor.fetchone()
    # check if user has already timed out
    if attendance.get('end_date') is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already timed out")
    # check if user has not timed in
    if not attendance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not timed in yet")
    
    cursor.execute("UPDATE attendance SET end_date = CURRENT_TIMESTAMP, total_hours = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_date)/3600) WHERE id = %s RETURNING *", (str(attendance.get('id')),))
    updated_attendance = cursor.fetchone()
    conn.commit()

    return updated_attendance