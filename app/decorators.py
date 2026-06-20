from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Restringe acesso conforme slug do perfil (legado)."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def permission_required(*codes):
    """Restringe acesso conforme permissões configuradas no perfil."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not any(current_user.has_permission(code) for code in codes):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
