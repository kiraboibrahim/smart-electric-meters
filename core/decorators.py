from functools import wraps

from django.db.utils import OperationalError


def ignore_table_does_not_exist_exception(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError:
            pass
    return decorator

