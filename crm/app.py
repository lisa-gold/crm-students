import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi_login import LoginManager
from crm.models import User
from crm.database import get_user
from crm.validation import validate_user


load_dotenv()


SECRET = os.getenv('SECRET')


app = FastAPI()
manager = LoginManager(SECRET, token_url='/auth/login')


@app.get("/")
def read_root():
    return {"introduction": "CRM students"}


@manager.user_loader()
def load_user(login):
    user = get_user(login)
    print(user)

    if not user:
        raise HTTPException(status_code=404,
                            detail={'error': 'no user with this login'})

    return user


@app.post("/auth/login")
def login(user_data: User):
    user = load_user(user_data.login)

    if not validate_user(user_data, user):
        return {'error': 'wrong password'}

    return user
