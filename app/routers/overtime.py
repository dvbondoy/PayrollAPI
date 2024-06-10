from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2, utils
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/overtime",
    tags=["Overtime"]
)

@router.get("/")
def get_overtimes(current_user: dict = Depends(oauth2.get_current_user)): 
    """
    Retrieve a list of all overtimes.

    Parameters:
    - current_user (dict): The current user object obtained from the OAuth2 authentication.

    Returns:
    - List[dict]: A list of dictionaries representing the overtimes.

    Raises:
    - HTTPException: If no overtimes are found, a 404 status code with the detail message "No overtimes found" is raised.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM overtime")
    overtimes = cursor.fetchall()
    if not overtimes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No overtimes found")
    
    return overtimes


@router.get("/{id}")
def get_overtime(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    """
    Retrieve overtime information by ID.

    Args:
        id (int): The ID of the overtime record to retrieve.
        current_user (dict): The current user's information.

    Returns:
        dict: The overtime record.

    Raises:
        HTTPException: If the overtime record is not found.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM overtime WHERE id = %s", (str(id),))
    overtime = cursor.fetchone()
    if not overtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Overtime not found")
    return overtime

# Apply for overtime
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_overtime(overtime: schemas.Overtime, current_user: dict = Depends(oauth2.get_current_user)):
    """
    Create a new overtime record in the database.

    Args:
        overtime (schemas.Overtime): The overtime data to be inserted.
        current_user (dict, optional): The current user information. Defaults to Depends(oauth2.get_current_user).

    Returns:
        dict: The newly created overtime record.

    Raises:
        HTTPException: If there is an error creating the overtime record.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    try:
        cursor.execute("""INSERT INTO overtime (employee_id, supervisor_id, start_date, end_date, total_hours, approved, attendance_date) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;""", 
                       (overtime.employee_id, overtime.supervisor_id, overtime.start_date, overtime.end_date, overtime.total_hours, overtime.approved, overtime.attendance_date))
        new_overtime = cursor.fetchone()
        conn.commit()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to create overtime: {e}")

    return new_overtime

@router.put("/{id}")
def update_overtime(id: int, overtime: schemas.OvertimeApproval, current_user: dict = Depends(oauth2.get_current_user)):
    """
    Update the overtime approval status for a specific overtime record.

    Args:
        id (int): The ID of the overtime record to update.
        overtime (schemas.OvertimeApproval): The updated overtime approval information.
        current_user (dict, optional): The current user information. Defaults to Depends(oauth2.get_current_user).

    Returns:
        dict: The updated overtime record.

    Raises:
        HTTPException: If the overtime record or attendance record is not found, or if there is an error updating the overtime record.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM overtime WHERE id = %s", (str(id),))
    existing_overtime = cursor.fetchone()
    if not existing_overtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Overtime not found")

    # get attendance record
    # cursor.execute("""SELECT * FROM attendance WHERE employee_id = %s AND DATE(start_date) = %s;""", (overtime.employee_id, overtime.attendance_date.date()))
    cursor.execute("""SELECT * FROM attendance WHERE employee_id = %s AND DATE(start_date) = %s;""", (existing_overtime['employee_id'], existing_overtime['attendance_date']))
    # print(cursor.query)
    attendance = cursor.fetchone()
    if not attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")

    try:
        cursor.execute("""UPDATE overtime SET approved = %s WHERE id = %s RETURNING *;""", (overtime.approved, str(id)))
        updated_overtime = cursor.fetchone()
        conn.commit()

        # update attendance record
        # cursor.execute("""UPDATE attendance SET overtime = %s WHERE employee_id = %s AND DATE(start_date) = %s;""", (overtime.total_hours, overtime.employee_id, overtime.attendance_date))
        cursor.execute("""UPDATE attendance SET overtime = %s WHERE employee_id = %s AND DATE(start_date) = %s;""", (existing_overtime['total_hours'], existing_overtime['employee_id'], existing_overtime['attendance_date']))

        conn.commit()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to update overtime: {e}")

    return updated_overtime