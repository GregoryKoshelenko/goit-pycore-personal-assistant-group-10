from functools import wraps


def with_session(func):
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        session = instance.session_factory()
        try:
            kwargs["session"] = session
            return func(instance, *args, **kwargs)
        finally:
            session.close()

    return wrapper
