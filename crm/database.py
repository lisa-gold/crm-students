from crm.models import User, Contact
import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB")


def get_db():
    try:
        cluster = MongoClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@{DB_NAME}')
        return cluster['crm']
    except Exception as e:
        print('No connection with the db', e)


DB = get_db()


# USERS
def get_user_by_login(login):
    # todo: password encoding
    user = DB['users'].find_one({"login": login})
    if user:
        return User(**user)
    return None


def add_user(user):
    if get_user_by_login(user.login):
        return False
    DB['users'].insert_one(user.__dict__)
    print('user added')
    return True


def get_users():
    return list(DB['users'].find({}, {'_id': False}))


def update_user(login, data):
    try:
        DB['users'].update_one({'login': login},
                               {'$set': data.dict(exclude_unset=True)})
        return True
    except Exception as e:
        print(e)
        return False


def delete_user(login):
    DB['users'].find_one_and_delete({'login': login})
    return True


# CONTACTS
def get_contacts():
    return list(DB['contacts'].find({'status': {'$nin': ['ARCHIVE']}},
                                    {'_id': False}))


def get_contact_by_id(id):
    contact = DB['contacts'].find_one({'id': int(id)}, {'_id': False})
    print(contact)
    if contact:
        return Contact(**contact)
    return None


def add_contact(data):
    if get_contact_by_id(data.id):
        return False
    if not data.id:
        data.id = (DB['contacts'].find_one(sort=[('id', -1)])['id']\
                   if DB['contacts'].find_one(sort=[('id', -1)]) else 0) + 1
    DB['contacts'].insert_one(data.__dict__)
    print("contact added")
    return True


def update_contact(id, data):
    try:
        DB['contacts'].update_one({'id': int(id)},
                                  {'$set': data.dict(exclude_unset=True)})
        return True
    except Exception as e:
        print(e)
        return False


def delete_contact(id):
    try:
        DB['contacts'].update_one({'id': int(id)},
                                  {'$set': {'status': "ARCHIVE"}})
        return True
    except Exception as e:
        print(e)
        return False


# COMMENTS IN CONTACTS
def add_comment(contact_id, data):
    contact = get_contact_by_id(contact_id)
    if not contact:
        return False
    contact.update({"comments": contact.comments + [data]})
    return update_contact(contact_id, contact)


def delete_comment(contact_id, comment):
    contact = get_contact_by_id(contact_id)
    if not contact:
        return False
    try:
        index = contact.comments.index(comment)
        contact.comments.pop(index)
        return update_contact(contact_id, contact)
    except ValueError:
        return False


# REMINDER
def add_reminder_to_contact(contact_id, data):
    contact = get_contact_by_id(contact_id)
    contact.update({'reminders': contact.reminders + [data]})
    return update_contact(contact_id, contact)


# STUDENTS
def get_students():
    return []  # todo: get them


def get_student_by_id(id):
    student = {}  # todo: get it
    return student


def add_student(data):
    # todo: add to db, check unique teudatZeut
    print('student added')
    return True


def update_student(id, data):
    student = get_student_by_id(id)
    student.update(data)
    # todo: block group update!
    # todo: update in db
    return True


def delete_student(id):
    # todo: archive, delete from archive?
    return True


# REMINDER
def add_reminder_to_student(student_id, data):
    student = get_student_by_id(student_id)
    student.update({'reminders': student.reminders + [data]})
    return update_student(student_id, student)


# GROUPS
def get_groups():
    return []  # todo: get them


def get_group_by_id(id):
    group = {}  # todo: get it
    return group


def add_group(data):
    # todo: add to db, check unique
    print('group added')
    return True


def update_group(id, data):
    group = get_group_by_id(id)
    group.update(data)
    # todo: update in db
    # todo: block updating studentsList
    return True


def add_student_to_group(group_id, student_id):
    student = get_student_by_id(student_id)
    group_new = get_group_by_id(group_id)
    group_history = student.groupsHistory
    if student.group:
        group_old = get_group_by_id(student.group.id)
        index = group_old.studentsList.find(student)
        group_old.studentsLis.pop(index)
        # update in the db old group
        group_history += [student.group]

    student.update({'group': group_new, 'groupsHistory': group_history})
    # update student in the db
    group_new.update({'studentsList': group_new.studentsList + [student]})
    # update new group in the db
    return True


def remove_student_from_group(group_id, student_id):
    student = get_student_by_id(student_id)
    group = get_group_by_id(group_id)
    index = group.studentsList.find(student)
    group.studentsLis.pop(index)
    # update in the db group
    student.update({'group': None,
                    'groupsHistory': student.group_history + [student.group],
                    'status': 'ARCHIVE'})
    # update student in the db
    return True


def delete_group(id):
    # todo: archive
    return True


# REMINDER
def add_reminder_to_group(id, data):
    group = get_group_by_id(id)
    group.update({'reminders': group.reminders + [data]})
    return update_group(id, group)
