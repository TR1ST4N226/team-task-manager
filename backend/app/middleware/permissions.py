from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.repositories.user_repository import UserRepository

def require_role(allowed_roles):
    """
    Decorator pour vérifier les rôles autorisés
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user_repo = UserRepository()
            user = user_repo.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role.value not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission):
    """
    Decorator pour vérifier des permissions spécifiques
    À étendre pour des permissions plus granulares
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Implémentation des permissions avancées
            # Exemple: vérifier si l'utilisateur peut modifier cette tâche
            return fn(*args, **kwargs)
        return wrapper
    return decorator