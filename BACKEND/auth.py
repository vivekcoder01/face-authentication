from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

def create_token(username, role):
    return create_access_token(identity={"username": username, "role": role})

def role_required(required_role):
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if identity["role"] != required_role:
                return {"msg": "Access denied"}, 403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator
