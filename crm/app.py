from fastapi import FastAPI
from crm.models import User


app = FastAPI()


@app.get("/")
def read_root():
    return {"introduction": "CRM students"}


@app.post("/auth/login")
def login(user_data: User):
    user = User()
    return user
