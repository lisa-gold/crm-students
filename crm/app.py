import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi_login import LoginManager
from datetime import timedelta, datetime
from crm.models import (
                        User, Contact, Comment,
                        Student, Reminder, Group
                        )
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
        if not user_data.login or not user_data.password:
            raise HTTPException(status_code=403,
                                detail={'error': 'login and password\
                                        are needed'})
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


@app.patch("/users/{user_login}")
def update_user(user_login, data: User, user=Depends(manager)):
    # login is not updatable
    if user.login == user_login or "ADMIN" in user.roles:
        if data.login and data.login != user_login:
            raise HTTPException(status_code=403,
                                detail={'error': 'login is not updatable'})
        db.update_user(user_login, data)
        return {"detail": "user updated successfully"}
    raise HTTPException(status_code=403,
                        detail={'error': 'if not admin, you can update\
                            only your data'})


@app.delete("/users/{user_login}")
def delete_user(user_login, user=Depends(manager)):
    if user.login == user_login or "ADMIN" in user.roles:
        # todo: add confirmation
        db.delete_user(user_login)
        return {"detail": "user deleted successfully"}
    raise HTTPException(status_code=403,
                        detail={'error': 'if not admin, you can delete\
                            only your account'})


# CONTACTS
@app.post("/contacts")
def add_contact(data: Contact, user=Depends(manager)):
    if db.add_contact(data):
        return {'detail': 'contact is added successfully'}
    raise HTTPException(status_code=403,
                        detail={'error': 'contact is NOT added'})


@app.get("/contacts")
def get_contacts(user=Depends(manager)):
    return db.get_contacts()


@app.get("/contacts/{id}")
def get_contact(id, user=Depends(manager)):
    contact = db.get_contact_by_id(id)
    if contact:
        return contact
    raise HTTPException(status_code=404,
                        detail={'error': f'no contact with id = {id}'})


@app.patch("/contacts/{id}")
def update_contacts(id, data: Contact, user=Depends(manager)):
    if db.update_contact(id, data):
        return {'detail': 'contact is updated successfully'}
    return {'error': 'contact is not updated'}


@app.delete("/contacts/{id}")
def delete_contact(id, user=Depends(manager)):
    # todo: confirmation
    if db.archive_contact(id):
        return {'detail': 'contact is deleted successfully'}
    return {'detail': 'contact is NOT deleted'}


# todo: get contacts from archive


# NEW (convert contact to student)
@app.post("/contacts/{id}/convert")
def convert_contact_to_student(id, data: Student, user=Depends(manager)):
    contact = db.get_contact_by_id(id)
    if not contact:
        raise HTTPException(status_code=404,
                            detail={'error': f'no contact with id = {id}'})
    student = contact.__dict__
    student.update(data.dict(exclude_unset=True))
    student = Student(**student)
    print(student)
    if db.add_student(student):
        db.delete_contact(id)
        return {'detail': 'contact is converted to student successfully'}
    return {'error': 'contact is NOT converted'}


# COMMENTS
@app.post("/contacts/{contact_id}/comments")
def add_comment(contact_id, data: Comment, user=Depends(manager)):
    if not db.get_contact_by_id(contact_id):
        raise HTTPException(status_code=404,
                            detail={'error': f'no contact with\
                                              id = {contact_id}'})
    data.addedBy = user.__dict__
    data.dateTime = datetime.now()
    if db.add_comment_to_contact(contact_id, data):
        return data


@app.delete("/contacts/{contact_id}/comments/{comment_id}")
def delete_comment(contact_id, comment_id, user=Depends(manager)):
    contact = db.get_contact_by_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404,
                            detail={'error': f'no contact with\
                                              id = {contact_id}'})

    if int(comment_id) >= len(contact.comments):
        raise HTTPException(status_code=404,
                            detail={'error': f'no comments with\
                                              id = {comment_id}'})

    if db.delete_comment_from_contact(contact_id, comment_id):
        return {'detail': 'comment is deleted successfully'}
    return {'detail': 'comment is NOT deleted'}


# REMINDER todo: delete reminders
@app.post("/contacts/{contact_id}/reminders")
def add_reminder_to_contact(contact_id, data: Reminder, user=Depends(manager)):
    if db.add_reminder_to_contact(contact_id, data):
        return {'detail': 'reminder is added successfully'}
    return {'detail': 'reminder is NOT added'}


# STUDENTS
@app.post("/students")
def add_student(data: Student, user=Depends(manager)):
    return db.add_student(data)


@app.get("/students")
def get_students(user=Depends(manager)):
    return db.get_students()


@app.get("/students/{id}")
def get_student(id, user=Depends(manager)):
    contact = db.get_student_by_id(id)
    if contact:
        return contact
    raise HTTPException(status_code=404,
                        detail={'error': f'no student with id = {id}'})


@app.put("/students/{id}")
def update_student(id, data: Student, user=Depends(manager)):
    if db.update_student(id, data):
        return data
    return {'error': 'student is not updated'}


@app.put("/students/{id}/move/{group_id}")
def move_student(id, group_id, user=Depends(manager)):
    if db.add_student_to_group(group_id, id):
        return {'detail': 'student is moved successfully'}

    return {'error': 'student is not moved'}


@app.delete("/students/{id}")
def delete_student(id, user=Depends(manager)):
    # todo: confirmation
    if db.delete_student(id):
        return {'detail': 'student is deleted successfully'}
    return {'detail': 'student is NOT deleted'}


# REMINDER todo: delete reminders
@app.post("/students/{student_id}/reminders")
def add_reminder_to_student(student_id, data: Reminder, user=Depends(manager)):
    if db.add_reminder_to_student(student_id, data):
        return {'detail': 'reminder is added successfully'}
    return {'detail': 'reminder is NOT added'}


# GROUPS
@app.post("/groups")
def add_group(data: Group, user=Depends(manager)):
    return db.add_group(data)


@app.get("/groups")
def get_groups(user=Depends(manager)):
    return db.get_groups()


@app.get("/groups/{id}")
def get_group(id, user=Depends(manager)):
    group = db.get_group_by_id(id)
    if group:
        return group
    raise HTTPException(status_code=404,
                        detail={'error': f'no group with id = {id}'})


@app.put("/groups/{id}")
def update_group(id, data: Group, user=Depends(manager)):
    if db.update_group(id, data):
        return data
    return {'error': 'group is not updated'}


@app.put("/groups/{id}/students/{student_id}")
def add_student_to_group(id, student_id, user=Depends(manager)):
    if db.add_student_to_group(id, student_id):
        return {'detail': 'student is added to the group successfully'}
    return {'error': 'student is not added to the group'}


@app.delete("/groups/{id}/students/{student_id}")
def delete_student_from_group(id, student_id, user=Depends(manager)):
    if db.remove_student_from_group(id, student_id):
        return {'detail': 'student is removed from the group successfully'}
    return {'error': 'student is not removed from the group'}


# REMINDER todo: delete reminders
@app.post("/groups/{id}/reminders")
def add_reminder_to_group(id, data: Reminder, user=Depends(manager)):
    if db.add_reminder_to_group(id, data):
        return {'detail': 'reminder is added successfully'}
    return {'detail': 'reminder is NOT added'}


@app.delete("/groups/{id}")
def delete_group(id, user=Depends(manager)):
    # todo: confirmation
    if db.delete_group(id):
        return {'detail': 'group is deleted successfully'}
    return {'detail': 'group is NOT deleted'}
