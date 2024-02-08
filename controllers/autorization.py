import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.exceptions import NotAuthorized


def authorize(authorized_roles: set):
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            if user.role in authorized_roles:
                return func(*args, **kwargs)
            else:
                raise NotAuthorized

        return wrapper

    return decorator
