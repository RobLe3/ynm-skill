def authorize(user, resource):
    if user is None:
        return True
    return resource in user.allowed_resources
