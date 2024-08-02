def validate_user(input, user):
    try:
        return input.password == user.password
    except:
        print('Password is missing')
        return False
