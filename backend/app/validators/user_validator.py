from typing import Dict, List
import re

class UserValidator:
    def validate_profile_update(self, data: Dict) -> List[str]:
        """
        Valide les données de mise à jour du profil
        """
        errors = []
        
        # Validation du username
        if data.get('username') is not None:
            if len(data['username']) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(data['username']) > 80:
                errors.append("Username must not exceed 80 characters")
            elif not re.match(r'^[a-zA-Z0-9_.-]+$', data['username']):
                errors.append("Username can only contain letters, numbers, underscores, dots and hyphens")
        
        # Validation du nom complet
        if data.get('full_name') is not None:
            if len(data['full_name']) < 2:
                errors.append("Full name must be at least 2 characters")
            elif len(data['full_name']) > 120:
                errors.append("Full name must not exceed 120 characters")
        
        # Validation de l'URL de l'avatar
        if data.get('avatar_url') is not None:
            if data['avatar_url'] and not self._validate_url(data['avatar_url']):
                errors.append("Invalid avatar URL format")
        
        return errors
    
    def validate_user_create(self, data: Dict) -> List[str]:
        """
        Valide les données de création d'un utilisateur (admin)
        """
        errors = []
        
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._validate_email(data['email']):
            errors.append("Invalid email format")
        
        if not data.get('username'):
            errors.append("Username is required")
        elif len(data['username']) < 3:
            errors.append("Username must be at least 3 characters")
        elif len(data['username']) > 80:
            errors.append("Username must not exceed 80 characters")
        
        if not data.get('password'):
            errors.append("Password is required")
        elif not self._validate_password(data['password']):
            errors.append("Password must be at least 8 characters with uppercase, lowercase, number and special character")
        
        if data.get('full_name') is not None:
            if len(data['full_name']) > 120:
                errors.append("Full name must not exceed 120 characters")
        
        # Validation du rôle
        if data.get('role'):
            if data['role'] not in ['admin', 'manager', 'member']:
                errors.append("Role must be one of: admin, manager, member")
        
        return errors
    
    def validate_user_update(self, data: Dict) -> List[str]:
        """
        Valide les données de mise à jour d'un utilisateur (admin)
        """
        errors = []
        
        if data.get('email') is not None:
            if not self._validate_email(data['email']):
                errors.append("Invalid email format")
        
        if data.get('username') is not None:
            if len(data['username']) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(data['username']) > 80:
                errors.append("Username must not exceed 80 characters")
        
        if data.get('full_name') is not None:
            if len(data['full_name']) > 120:
                errors.append("Full name must not exceed 120 characters")
        
        if data.get('role') is not None:
            if data['role'] not in ['admin', 'manager', 'member']:
                errors.append("Role must be one of: admin, manager, member")
        
        if data.get('is_active') is not None:
            if not isinstance(data['is_active'], bool):
                errors.append("is_active must be a boolean")
        
        return errors
    
    def validate_password_reset(self, data: Dict) -> List[str]:
        """
        Valide les données de réinitialisation de mot de passe
        """
        errors = []
        
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._validate_email(data['email']):
            errors.append("Invalid email format")
        
        return errors
    
    def validate_password_update(self, data: Dict) -> List[str]:
        """
        Valide les données de mise à jour du mot de passe
        """
        errors = []
        
        if not data.get('current_password'):
            errors.append("Current password is required")
        
        if not data.get('new_password'):
            errors.append("New password is required")
        elif not self._validate_password(data['new_password']):
            errors.append("Password must be at least 8 characters with uppercase, lowercase, number and special character")
        
        if data.get('new_password') and data.get('current_password'):
            if data['new_password'] == data['current_password']:
                errors.append("New password must be different from current password")
        
        if data.get('confirm_password') is not None:
            if data['new_password'] != data['confirm_password']:
                errors.append("Passwords do not match")
        
        return errors
    
    def _validate_email(self, email: str) -> bool:
        """
        Valide le format d'un email
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password: str) -> bool:
        """
        Valide la force d'un mot de passe
        """
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
    
    def _validate_url(self, url: str) -> bool:
        """
        Valide le format d'une URL
        """
        pattern = r'^https?://[a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=]+$'
        return re.match(pattern, url) is not None
    
    def validate_team_member_add(self, data: Dict) -> List[str]:
        """
        Valide l'ajout d'un membre à une équipe
        """
        errors = []
        
        if not data.get('user_id'):
            errors.append("User ID is required")
        elif not isinstance(data['user_id'], int):
            errors.append("User ID must be an integer")
        
        if data.get('role') is not None:
            if data['role'] not in ['admin', 'manager', 'member']:
                errors.append("Role must be one of: admin, manager, member")
        
        return errors
    
    def validate_bulk_user_import(self, data: Dict) -> List[str]:
        """
        Valide l'importation massive d'utilisateurs
        """
        errors = []
        
        if not data.get('users'):
            errors.append("Users list is required")
        elif not isinstance(data['users'], list):
            errors.append("Users must be a list")
        else:
            for idx, user_data in enumerate(data['users']):
                # Vérifier que chaque utilisateur a les champs requis
                if not user_data.get('email'):
                    errors.append(f"User at index {idx}: Email is required")
                elif not self._validate_email(user_data['email']):
                    errors.append(f"User at index {idx}: Invalid email format")
                
                if not user_data.get('username'):
                    errors.append(f"User at index {idx}: Username is required")
                elif len(user_data['username']) < 3:
                    errors.append(f"User at index {idx}: Username must be at least 3 characters")
                
                if not user_data.get('password'):
                    errors.append(f"User at index {idx}: Password is required")
                elif not self._validate_password(user_data['password']):
                    errors.append(f"User at index {idx}: Password must be at least 8 characters with uppercase, lowercase, number and special character")
        
        return errors
    
    def validate_user_search(self, data: Dict) -> List[str]:
        """
        Valide les paramètres de recherche d'utilisateurs
        """
        errors = []
        
        if data.get('query') is not None:
            if len(data['query']) < 2:
                errors.append("Search query must be at least 2 characters")
        
        if data.get('limit') is not None:
            if not isinstance(data['limit'], int) or data['limit'] < 1:
                errors.append("Limit must be a positive integer")
            elif data['limit'] > 100:
                errors.append("Limit must not exceed 100")
        
        if data.get('offset') is not None:
            if not isinstance(data['offset'], int) or data['offset'] < 0:
                errors.append("Offset must be a non-negative integer")
        
        if data.get('role') is not None:
            if data['role'] not in ['admin', 'manager', 'member']:
                errors.append("Role must be one of: admin, manager, member")
        
        if data.get('is_active') is not None:
            if not isinstance(data['is_active'], bool):
                errors.append("is_active must be a boolean")
        
        return errors