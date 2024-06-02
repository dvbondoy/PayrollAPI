from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi import HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from .config import settings
from .dbase import cursor, conn

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expiration

def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = payload.get("employee_id")
        if employee_id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=employee_id)
        
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_token(token, credentials_exception)

    cursor.execute("SELECT * FROM employee WHERE id = %s", (token.id,))
    employee = cursor.fetchone()

    cursor.execute("SELECT role FROM role WHERE employee_id = %s", (token.id,))
    roles = cursor.fetchall()
    # user_roles = []
    # for role in roles:
    #     user_roles.append(role['role'])
    # print(list(employee.keys()))
    user_roles = [role.get('role') for role in roles]
    # for role in roles:
    #     print(role.get('role'))

    result = {'id': employee.get('id'), 'roles':user_roles}

    # print (result)

    return result

# check permissions
def check_permissions(current_user: dict, permissions: list):
    authorized = False
    for role in permissions:
        if role in current_user.get('roles'):
            authorized = True
            break
    
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")

