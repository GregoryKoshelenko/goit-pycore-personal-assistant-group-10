from functools import wraps


def with_session(func):
    """Inject a SQLAlchemy session into the wrapped provider method."""
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        """Open, pass, and close a session around one call."""
        session = instance.session_factory()
        try:
            kwargs["session"] = session
            return func(instance, *args, **kwargs)
        finally:
            session.close()

    return wrapper
