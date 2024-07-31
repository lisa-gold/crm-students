import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi_login import LoginManager
from datetime import timedelta
from crm.models import User
import crm.database as db
from crm.validation import validate_user


load_dotenv()


SECRET = os.getenv('SECRET')


app = FastAPI()
manager = LoginManager(SECRET, token_url='/auth/login')


@app.get("/")
def read_root():
    return {"introduction": "CRM students"}


# USERS
@manager.user_loader()
def load_user(login):
    user = db.get_user_by_login(login)

    if not user:
        raise HTTPException(status_code=404,
                            detail={'error': 'no user with this login'})

    return user


@app.post("/auth/login")
def login(user_data: User):
    user = load_user(user_data.login)

    if not validate_user(user_data, user):
        return {'error': 'wrong password'}

    access_token = manager.create_access_token(
        data=dict(sub=user_data.login),
        expires=timedelta(hours=9)  # log out in 9 hours
    )
    return {"token": access_token,
            "token_type": "bearer",
            "user": user}


@app.post("/auth/logout")
def logout():
    # todo: add tokens to blacklist
    return {'details': 'logged out'}


@app.post("/auth/register")
def register(user_data: User, user_admin=Depends(manager)):
    # random user cannot register
    if "ADMIN" in user_admin.roles:
        if db.add_user(user_data):
            return user_data
        raise HTTPException(status_code=403,
                            detail={'error': f'user {user_data.login}\
                                    already exists'})
    raise HTTPException(status_code=403,
                        detail={'error': 'only admins can register users'})


@app.get("/users")
def get_users(user=Depends(manager)):
    return db.get_users()


@app.get("/users/{user_login}")
def get_user(user_login, user=Depends(manager)):
    return db.get_user_by_login(user_login)


@app.put("/users/{user_login}")
def update_user(user_login, data, user=Depends(manager)):
    # login is not updatable !!!
    if user.login == user_login or "ADMIN" in user.roles:
        db.update_user(user_login, data)
        return {"detail": "user updated successfully"}
    raise HTTPException(status_code=403,
                        detail={'error': 'if not admin, you can update\
                            only your data'})


@app.delete("/users/{user_login}")
def delete_user(user_login, user=Depends(manager)):
    if user.login == user_login or "ADMIN" in user.roles:
        # todo: add confirmation !
        db.delete_user(user_login)
        return {"detail": "user updated successfully"}
    raise HTTPException(status_code=403,
                        detail={'error': 'if not admin, you can delete\
                            only your account'})
