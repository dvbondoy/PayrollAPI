from app import schemas, oauth2, utils
from fastapi import Depends, HTTPException, status, APIRouter
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)

@router.get("/")
def get_employees(current_user:int = Depends(oauth2.get_current_user)) -> list[schemas.EmployeeResponse]:
   # set and check permissions
    oauth2.check_permissions(current_user, ['admin','user'])
        
    cursor.execute("SELECT * FROM employee")
    employees = cursor.fetchall()
    return employees

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.Employee):
    employee.password = utils.hash(employee.password)
    cursor.execute("""INSERT INTO employee (firstname, lastname, middlei, address, id_number, password, gender, birthday, \
                   phone_number, employment_status, position, supervisor_id, basic_salary, gsm_rate, hourly_rate) \
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING * """, 
                   (employee.firstname, employee.lastname, employee.middlei, employee.address, employee.id_number,
                    employee.password,employee.gender,employee.birthday,employee.phone_number,employee.employment_status,
                    employee.position,employee.supervisor_id,employee.basic_salary,employee.gsm_rate,employee.hourly_rate))
    
    new_employee = cursor.fetchone()
    conn.commit()

    return new_employee

@router.get("/{id}")
def get_employee(id: int, current_user: dict = Depends(oauth2.get_current_user)) -> schemas.EmployeeResponse:
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    # get employee
    cursor.execute("SELECT * FROM employee WHERE id = %s", (str(id),))
    employee = cursor.fetchone()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee not found")
    
    return employee

@router.put("/{id}")
def update_employee(id: int, employee: schemas.Employee):
    cursor.execute("UPDATE employee SET firstname = %s, lastname = %s, middlei = %s, \
                   address = %s WHERE id = %s RETURNING *", (employee.firstname, employee.lastname, \
                    employee.middlei, employee.address, str(id)))
    updated_employee = cursor.fetchone()
    conn.commit()

    if updated_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {id} not found")
    
    return updated_employee

@router.delete("/{id}")
def delete_employee(id: int):
    cursor.execute("DELETE FROM employee WHERE id = %s RETURNING *", (str(id),))
    deleted_employee = cursor.fetchone()
    conn.commit()

    if deleted_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {id} not found")
    
    return f"Employee with id {id} has been deleted"