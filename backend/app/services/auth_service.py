from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app import bcrypt
import re

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.user_service = UserService()
    
    def register(self, email: str, username: str, password: str, full_name: str = None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Inscription d'un nouvel utilisateur
        Retourne: (user_data, error_message)
        """
        # Validation
        if not self._validate_email(email):
            return None, "Invalid email format"
        
        if not self._validate_password(password):
            return None, "Password must be at least 8 characters with uppercase, lowercase, number and special character"
        
        if len(username) < 3:
            return None, "Username must be at least 3 characters"
        
        # Vérifier si l'email ou username existe déjà
        if self.user_repository.find_by_email(email):
            return None, "Email already registered"
        
        if self.user_repository.find_by_username(username):
            return None, "Username already taken"
        
        # Hasher le mot de passe
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Créer l'utilisateur
        user = self.user_repository.create({
            'email': email,
            'username': username,
            'password_hash': password_hash,
            'full_name': full_name or username
        })
        
        return user.to_dict(), None
    
    def login(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Connexion d'un utilisateur
        Retourne: (tokens_data, error_message)
        """
        user = self.user_repository.find_by_email(email)
        
        if not user:
            return None, "Invalid credentials"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        # Vérifier le mot de passe
        if not bcrypt.check_password_hash(user.password_hash, password):
            return None, "Invalid credentials"
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        self.user_repository.update(user.id, {'last_login': user.last_login})
        
        # Générer les tokens - MODIFICATION: identity doit être un string
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'role': user.role.value if user.role else 'member'
            }
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, None
    
    def refresh_token(self, user_id: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Rafraîchit le token d'accès
        """
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.is_active:
            return None, "User not found or inactive"
        
        # MODIFICATION: identity doit être un string
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'role': user.role.value if user.role else 'member'
            }
        )
        
        return access_token, None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change le mot de passe d'un utilisateur
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Vérifier l'ancien mot de passe
        if not bcrypt.check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect"
        
        # Valider le nouveau mot de passe
        if not self._validate_password(new_password):
            return False, "Password must be at least 8 characters with uppercase, lowercase, number and special character"
        
        # Hasher le nouveau mot de passe
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        self.user_repository.update(user_id, {'password_hash': new_password_hash})
        
        return True, None
    
    def reset_password(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Réinitialise le mot de passe (envoie un email de réinitialisation)
        """
        user = self.user_repository.find_by_email(email)
        if not user:
            return False, "Email not found"
        
        # TODO: Implémenter l'envoi d'email de réinitialisation
        # Générer un token de réinitialisation
        # Envoyer l'email avec le lien
        
        return True, None
    
    def _validate_email(self, email: str) -> bool:
        """Valide le format de l'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password: str) -> bool:
        """Valide la force du mot de passe"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True