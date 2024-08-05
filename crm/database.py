from crm.models import User, Contact, Student, Group
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
    if contact:
        return Contact(**contact)
    return None


def add_contact(data):
    if data.id and get_contact_by_id(data.id):
        return False
    if not data.id:
        id = 0
        if DB['students'].find_one(sort=[('id', -1)]):
            id = DB['students'].find_one(sort=[('id', -1)])['id'] + 1

        if DB['contacts'].find_one(sort=[('id', -1)]):
            id = max(id, DB['contacts'].find_one(sort=[('id', -1)])['id'] + 1)

        data.id = id

    DB['contacts'].insert_one(data.__dict__)
    print("contact added")
    return True


def update_contact(id, data):
    if data.comments:
        print('Use "/contacts/{contact_id}/comments" to add/delete comments')
        return False
    if data.reminders:
        print('Use "/contacts/{contact_id}/reminders" to add/delete reminders')
        return False
    if data.id and data.id != id:
        print('Cannot change id')
        return False
    try:
        DB['contacts'].update_one({'id': int(id)},
                                  {'$set': data.dict(exclude_unset=True)})
        return True
    except Exception as e:
        print(e)
        return False


def archive_contact(id):
    try:
        DB['contacts'].update_one({'id': int(id)},
                                  {'$set': {'status': "ARCHIVE"}})
        return True
    except Exception as e:
        print(e)
        return False


def delete_contact(id):
    DB['contacts'].find_one_and_delete({'id': int(id)})
    return True


# COMMENTS IN CONTACTS
def add_comment_to_contact(contact_id, data):
    contact = get_contact_by_id(contact_id)
    if not contact:
        print(f'contact with id = {contact_id} not found')
        return False
    try:
        DB['contacts'].update_one({'id': int(contact_id)},
                                  {'$push': {'comments': data.__dict__}})
        return True
    except Exception as e:
        print(e)
        return False


def delete_comment_from_contact(contact_id, comment_id):
    contact = get_contact_by_id(contact_id)
    if not contact:
        print(f'contact with id = {contact_id} not found')
        return False
    try:
        comment = list(contact.comments)[int(comment_id)]
        print(comment.__dict__)
        DB['contacts'].update_one({'id': int(contact_id)},
                                  {'$pull': {'comments': {
                                                'comment': comment.comment,
                                                'details': comment.details,
                                                'dateTime': comment.dateTime
                                                }
                                             }
                                   }
                                  )
        return True
    except IndexError:
        print('this comment is not found')
        return False


# REMINDER
def add_reminder_to_contact(contact_id, data):
    contact = get_contact_by_id(contact_id)
    if not contact:
        print(f'contact with id = {contact_id} not found')
        return False
    try:
        DB['contacts'].update_one({'id': int(contact_id)},
                                  {'$push': {'reminders': data.__dict__}})
        return True
    except Exception as e:
        print(e)
        return False


# STUDENTS
def get_students():
    return list(DB['students'].find({'status': {'$nin': ['ARCHIVE']}},
                                    {'_id': False}))


def get_student_by_id(id):
    student = DB['students'].find_one({"id": int(id)}, {'_id': False})
    if student:
        return Student(**student)
    return None


def add_student(data):
    if data.teudatZeut and\
            DB['students'].find_one({'teudatZeut': int(data.teudatZeut)}):
        print(f'Student with TZ {data.teudatZeut} already exists')
        return False
    if data.id and get_student_by_id(data.id):
        print(f'Student with id = {data.id} already exists')
        return False
    if not data.id:
        id = 0
        if DB['students'].find_one(sort=[('id', -1)]):
            id = DB['students'].find_one(sort=[('id', -1)])['id'] + 1

        if DB['contacts'].find_one(sort=[('id', -1)]):
            id = max(id, DB['contacts'].find_one(sort=[('id', -1)])['id'] + 1)

        data.id = id
    group_id = data.group
    data.group = None
    DB['students'].insert_one(data.__dict__)
    if group_id:
        add_student_to_group(group_id, data.id)
    print('student added')
    return True


def update_student(id, data):
    student = get_student_by_id(id)
    if student.group != data.group or\
            student.groupsHistory != data.groupsHistory:
        print("You cannot change student's groups this way.\
               Use '/students/{student_id}/move/{group_id}'")
        return False

    try:
        DB['students'].update_one({'id': int(id)},
                                  {'$set': data.dict(exclude_unset=True)})
        return True
    except Exception as e:
        print(e)
        return False


def delete_student(id):
    try:
        DB['students'].update_one({'id': int(id)},
                                  {'$set': {'status': "ARCHIVE"}})
        student = get_student_by_id(id)
        if student.group:
            remove_student_from_group(student.group, id)
        return True
    except Exception as e:
        print(e)
        return False


# REMINDER
def add_reminder_to_student(student_id, data):
    student = get_student_by_id(student_id)
    if not student:
        print(f'student with id = {student_id} not found')
        return False
    try:
        DB['students'].update_one({'id': int(student_id)},
                                  {'$push': {'reminders': data.__dict__}})
        return True
    except Exception as e:
        print(e)
        return False


# GROUPS
def get_groups():
    return list(DB['groups'].find({'active': True},
                                  {'_id': False}))


def get_group_by_id(id):
    group = DB['groups'].find_one({"id": int(id)}, {'_id': False})
    if group:
        return Group(**group)
    return None


def add_group(data):
    if data.id and DB['groups'].find_one({'id': int(data.id)}):
        print(f'Group with id = {data.id} already exists')
        return False

    if not data.id:
        data.id = DB['groups'].find_one(sort=[('id', -1)])['id'] + 1\
            if DB['groups'].find_one(sort=[('id', -1)]) else 1

    DB['groups'].insert_one(data.__dict__)
    for student_id in data.studentsList:
        add_student_to_group(data.id, student_id)
    print('group added')
    return True


def update_group(id, data):
    group = get_group_by_id(id)
    if data.studentsList and group.studentsList != data.studentsList:
        print('Use "/groups/{group_id}/students/{student_id}"\
               to change students list')
        return False

    try:
        DB['groups'].update_one({'id': int(id)},
                                {'$set': data.dict(exclude_unset=True)})
        return True

    except Exception as e:
        print(e)
        return False


def add_student_to_group(group_id, student_id):
    student = get_student_by_id(student_id)
    if not student:
        print(f'No student with id = {student_id}')
        return False
    group = get_group_by_id(group_id)
    if not group:
        print(f'No group with id = {group_id}')
        return False

    if student.group:
        if student.group == int(group_id):
            print('Cannot move to the same group')
            return False
        DB['groups'].update_one({'id': int(student.group)},
                                {'$pull':
                                    {'studentsList': int(student_id)}})
        DB['students'].update_one({'id': int(student_id)},
                                  {'$push': {'groupsHistory': int(student.group)}})

    DB['students'].update_one({'id': int(student_id)},
                              {'$set': {'group': int(group_id)}})
    
    DB['groups'].update_one({'id': int(group_id)},
                            {'$push':
                                {'studentsList': int(student_id)}})
    return True


def remove_student_from_group(group_id, student_id):

    # update in the db group
    DB['groups'].update_one({'id': int(group_id)},
                            {'$pull': {'studentsList': int(student_id)}})

    DB['students'].update_one({'id': int(student_id)},
                              {'$set':
                                  {'group': None,
                                   'status': 'ARCHIVE'},
                               '$push':
                                   {'groupsHistory': int(group_id)}})
    return True


def delete_group(id):
    try:
        DB['groups'].update_one({'id': int(id)},
                                {'$set': {'active': False}})
        return True
    except Exception as e:
        print(e)
        return False


# REMINDER
def add_reminder_to_group(id, data):
    group = get_group_by_id(id)
    if not group:
        print(f'group with id = {id} not found')
        return False
    try:
        DB['groups'].update_one({'id': int(id)},
                               {'$push': {'reminders': data.__dict__}})
        return True
    except Exception as e:
        print(e)
        return False
