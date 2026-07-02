from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from flask import jsonify

# Ces fonctions sont importées directement depuis flask_jwt_extended
# Nous les réexportons pour une meilleure organisation

__all__ = ['jwt_required', 'get_jwt_identity', 'get_jwt']

# Custom wrapper pour vérifier les rôles
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', 'member')
            
            # Vérifier les permissions
            if required_role == 'admin' and user_role != 'admin':
                return jsonify({'error': 'Admin permission required'}), 403
            elif required_role == 'manager' and user_role not in ['admin', 'manager']:
                return jsonify({'error': 'Manager permission required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper