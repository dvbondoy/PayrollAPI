from fastapi import FastAPI
# fastapi middleware for cors
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
# import routers
from .routers import employee, auth, rol, attendance, payroll


# not needed with alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# fastapi middleware for cors
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(employee.router)
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(rol.router)
app.include_router(payroll.router)

# root route
@app.get("/")
def root():
    return {"data": "Hello World"}

# startup event
@app.on_event("startup")
def startup():
    print ("Starting up")
    # users = user.get_users()
    # print(users)