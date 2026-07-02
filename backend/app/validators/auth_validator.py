import re
from typing import Dict, List

class AuthValidator:
    def validate_register(self, data: Dict) -> List[str]:
        """Valide les données d'inscription"""
        errors = []
        
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._validate_email(data['email']):
            errors.append("Invalid email format")
        
        if not data.get('username'):
            errors.append("Username is required")
        elif len(data['username']) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not data.get('password'):
            errors.append("Password is required")
        elif not self._validate_password(data['password']):
            errors.append("Password must be at least 8 characters with uppercase, lowercase, number and special character")
        
        return errors
    
    def validate_login(self, data: Dict) -> List[str]:
        """Valide les données de connexion"""
        errors = []
        
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._validate_email(data['email']):
            errors.append("Invalid email format")
        
        if not data.get('password'):
            errors.append("Password is required")
        
        return errors
    
    def validate_password_change(self, data: Dict) -> List[str]:
        """Valide le changement de mot de passe"""
        errors = []
        
        if not data.get('old_password'):
            errors.append("Current password is required")
        
        if not data.get('new_password'):
            errors.append("New password is required")
        elif not self._validate_password(data['new_password']):
            errors.append("New password must be at least 8 characters with uppercase, lowercase, number and special character")
        
        if data.get('new_password') and data.get('old_password'):
            if data['new_password'] == data['old_password']:
                errors.append("New password must be different from current password")
        
        return errors
    
    def _validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password: str) -> bool:
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