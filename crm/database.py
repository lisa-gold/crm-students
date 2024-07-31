from crm.models import User


ADMIN = {'login': 'toto',
         'password': '123',
         "firstName": "to",
         "lastName": "surname",
         "roles": ["ADMIN", "USER"]}
USER = {
    "login": "fefe",
    "password": "321",
    "firstName": "fe",
    "lastName": "surname",
    "roles": ["USER"]
}


# USERS
def get_user_by_login(login):
    # todo: get user from db
    # todo: password encoding
    user = USER
    if login == user['login']:
        return User(**user)
    return None


def add_user(user):
    # todo: add user to db
    # check if unique
    print('user added')
    return True


def get_users():
    # todo: get users from db
    return [ADMIN, USER]


def update_user(login, data):
    # todo: update user
    user = get_user_by_login(login)
    user.update(data)
    # todo: update in db
    return True


def delete_user(login):
    # todo: delete user
    return True


# CONTACTS
def get_contacts():
    return []  # todo: get them


def get_contacts_by_id(id):
    contact = {}  # todo: get it
    return contact


def add_contact(data):
    # todo: add
    print("contact added")
    return True


def update_contact(id, data):
    contact = get_contacts_by_id(id)
    contact.update(data)
    # todo: update in db
    return True


def delete_contact(id):
    # todo: archive contact
    return True


# COMMENTS IN CONTACTS
def add_comment(contact_id, data):
    contact = get_contacts_by_id(contact_id)
    if not contact:
        return False
    contact.update({"comments": contact.comments + [data]})
    return update_contact(contact_id, contact)


def delete_comment(contact_id, comment):
    contact = get_contacts_by_id(contact_id)
    if not contact:
        return False
    try:
        index = contact.comments.index(comment)
        contact.comments.pop(index)
        return update_contact(contact_id, contact)
    except ValueError:
        return False
