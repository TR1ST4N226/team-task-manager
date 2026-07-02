from typing import Dict, List

class TeamValidator:
    def validate_create(self, data: Dict) -> List[str]:
        """Valide les données de création d'une équipe"""
        errors = []
        
        if not data.get('name'):
            errors.append("Team name is required")
        elif len(data['name']) < 3:
            errors.append("Team name must be at least 3 characters")
        elif len(data['name']) > 100:
            errors.append("Team name must not exceed 100 characters")
        
        if data.get('description') and len(data['description']) > 500:
            errors.append("Description must not exceed 500 characters")
        
        return errors
    
    def validate_update(self, data: Dict) -> List[str]:
        """Valide les données de mise à jour d'une équipe"""
        errors = []
        
        if data.get('name') is not None:
            if len(data['name']) < 3:
                errors.append("Team name must be at least 3 characters")
            elif len(data['name']) > 100:
                errors.append("Team name must not exceed 100 characters")
        
        if data.get('description') is not None and len(data['description']) > 500:
            errors.append("Description must not exceed 500 characters")
        
        return errors
    
    def validate_member_role(self, data: Dict) -> List[str]:
        """Valide le rôle d'un membre"""
        errors = []
        
        if not data.get('role'):
            errors.append("Role is required")
        elif data['role'] not in ['admin', 'manager', 'member']:
            errors.append("Role must be one of: admin, manager, member")
        
        return errors