from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2
from app.dbase import conn, cursor

router = APIRouter(
    prefix="/role",
    tags=["Role"]
)

@router.get("/")
def get_roles(current_user: dict = Depends(oauth2.get_current_user)):# -> list[schemas.RoleResponse]:
    cursor.execute("SELECT role.id, role.role, role.description, employee.firstname, employee.lastname FROM role INNER JOIN employee ON role.employee_id = employee.id WHERE role.employee_id = %s", (str(current_user.get('id'))))
    roles = cursor.fetchall()
    return roles

@router.get("/{id}")
def get_role(id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("SELECT * FROM role WHERE id = %s", (str(id),))
    role = cursor.fetchone()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role {id} not found")
    
    return role

@router.get("/search")
def search_roles(search: str, current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
    cursor.execute("SELECT * FROM role WHERE role ILIKE %s", (f"%{search}%",))
    roles = cursor.fetchall()
    return roles

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_role(role: schemas.Role, current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.get("id"))
    # check if role already exists
    cursor.execute("SELECT * FROM role WHERE role = %s AND employee_id = %s", (role.role, str(current_user.get("id"))))
    if cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    # create new role
    cursor.execute("INSERT INTO role (role, description, employee_id) VALUES (%s, %s, %s) RETURNING *", (role.role, role.description, str(current_user.get("id"))))
    new_role = cursor.fetchone()
    conn.commit()

    return new_role

@router.delete("/{id}")
def delete_role(id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("DELETE FROM role WHERE id = %s AND employee_id = %s RETURNING *", (str(id), str(current_user.get('id'))))
    deleted_role = cursor.fetchone()
    conn.commit()

    if not deleted_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role {id} not found")

    return {"data": f"Role {id} deleted"}