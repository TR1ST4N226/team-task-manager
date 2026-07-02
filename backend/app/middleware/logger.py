from functools import wraps
from flask import request, g
from app.services.activity_service import ActivityService
from flask_jwt_extended import get_jwt_identity
import logging
import json
from datetime import datetime

# Configuration du logger
logger = logging.getLogger(__name__)

def log_request(fn):
    """
    Middleware pour logger les requêtes entrantes
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Log de la requête
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        if request.data:
            try:
                logger.info(f"Body: {json.loads(request.data)}")
            except:
                logger.info(f"Body: {request.data}")
        
        # Stocker le temps de début pour mesurer la performance
        g.start_time = datetime.utcnow()
        
        return fn(*args, **kwargs)
    return wrapper

def log_response(fn):
    """
    Middleware pour logger les réponses
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        
        # Log de la réponse
        logger.info(f"Response: {response.status_code} for {request.path}")
        
        # Mesurer le temps de réponse
        if hasattr(g, 'start_time'):
            elapsed = (datetime.utcnow() - g.start_time).total_seconds()
            logger.info(f"Response time: {elapsed:.3f}s")
        
        return response
    return wrapper

def log_activity(action):
    """
    Decorator pour logger automatiquement une activité
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Récupérer l'utilisateur si authentifié
            user_id = None
            try:
                user_id = get_jwt_identity()
            except:
                pass
            
            # Exécuter la fonction
            result = fn(*args, **kwargs)
            
            # Logger l'activité si on a un utilisateur
            if user_id:
                activity_service = ActivityService()
                activity_service.log_activity(
                    user_id=user_id,
                    action=action,
                    details={
                        'path': request.path,
                        'method': request.method,
                        'args': kwargs
                    },
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
            
            return result
        return wrapper
    return decorator