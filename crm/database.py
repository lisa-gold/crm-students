from crm.models import User


def get_user(login):
    # todo: get user from db
    # todo: password encoding
    user = {'login': 'toto',
            'password': '123',
            "firstName": "to",
            "lastName": "surname"}
    if login == user['login']:
        return User(**user)
    return None
