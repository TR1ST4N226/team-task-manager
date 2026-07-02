from typing import Dict, List

class CommentValidator:
    def validate_create(self, data: Dict) -> List[str]:
        """Valide les données de création d'un commentaire"""
        errors = []
        
        if not data.get('task_id'):
            errors.append("Task ID is required")
        
        if not data.get('content'):
            errors.append("Comment content is required")
        elif len(data['content']) < 1:
            errors.append("Comment must not be empty")
        elif len(data['content']) > 5000:
            errors.append("Comment must not exceed 5000 characters")
        
        return errors
    
    def validate_update(self, data: Dict) -> List[str]:
        """Valide les données de mise à jour d'un commentaire"""
        errors = []
        
        if not data.get('content'):
            errors.append("Comment content is required")
        elif len(data['content']) < 1:
            errors.append("Comment must not be empty")
        elif len(data['content']) > 5000:
            errors.append("Comment must not exceed 5000 characters")
        
        return errors