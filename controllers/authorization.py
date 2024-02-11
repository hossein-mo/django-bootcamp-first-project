import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.utils import create_response

def authorize(authorized_roles: set):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = args[0]
            if user.role in authorized_roles:
                return func(*args, **kwargs)
            else:
                return create_response(False, "user", 'User not authorized for this action.')

        return wrapper

    return decorator
