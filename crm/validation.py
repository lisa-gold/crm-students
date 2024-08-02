def validate_user(input, user):
    try:
        return input.password == user.password
    except Exception as e:
        print('Password is missing', e)
        return False
