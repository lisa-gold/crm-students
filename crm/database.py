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
    return [ADMIN, USER]
