from .. import schemas, oauth2, utils
from fastapi import Depends, HTTPException, status, APIRouter
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# get all attendance
@router.get("/all")
def get_attendance(current_user:int = Depends(oauth2.get_current_user), limit: int = 50, skip: int = 0):
    oauth2.check_permissions(current_user, ['hr','finance','admin'])
    cursor.execute("SELECT * FROM attendance limit %s offset %s", (limit, skip))
    attendance = cursor.fetchall()
    return attendance

# get attendance by current user
@router.get("/user")
def get_attendance_by_current_user(current_user: int = Depends(oauth2.get_current_user), limit: int = 50, skip: int = 0):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s", (str(current_user.get('id')),))
    attendance = cursor.fetchall()
    return attendance

# clock in current user
@router.post("/timein")
def time_in(current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND date = CURRENT_DATE", (str(current_user.get('id'))))
    attendance = cursor.fetchone()
    if attendance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already timed in")
    
    cursor.execute("INSERT INTO attendance (employee_id, time_in, date) VALUES (%s, CURRENT_TIME, CURRENT_DATE) RETURNING *", (str(current_user.get('id')),))
    new_attendance = cursor.fetchone()
    conn.commit()

    return new_attendance

# clock out current user
@router.post("/timeout")
def time_out(current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND date = CURRENT_DATE;", (str(current_user.get('id')),))
    attendance = cursor.fetchone()
    # check if user has already timed out
    if attendance.get('time_out') is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already timed out")
    # check if user has not timed in
    if not attendance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not timed in yet")
    
    cursor.execute("UPDATE attendance SET time_out = CURRENT_TIME WHERE id = %s RETURNING *", (str(attendance.get('id')),))
    updated_attendance = cursor.fetchone()
    conn.commit()

    return updated_attendance