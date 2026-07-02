from typing import Dict, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

class TaskValidator:
    def validate_create(self, data: Dict) -> List[str]:
        """Valide les données de création d'une tâche"""
        errors = []
        
        if not data.get('title'):
            errors.append("Title is required")
        elif len(data['title']) < 3:
            errors.append("Title must be at least 3 characters")
        elif len(data['title']) > 200:
            errors.append("Title must not exceed 200 characters")
        
        if data.get('status'):
            if data['status'] not in [s.value for s in TaskStatus]:
                errors.append(f"Invalid status. Must be one of: {', '.join([s.value for s in TaskStatus])}")
        
        if data.get('priority'):
            if data['priority'] not in [p.value for p in TaskPriority]:
                errors.append(f"Invalid priority. Must be one of: {', '.join([p.value for p in TaskPriority])}")
        
        if data.get('due_date'):
            try:
                datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except:
                errors.append("Invalid due_date format. Use ISO 8601 format")
        
        if data.get('estimated_hours') is not None:
            if not isinstance(data['estimated_hours'], (int, float)) or data['estimated_hours'] < 0:
                errors.append("Estimated hours must be a positive number")
        
        if data.get('assignee_ids') is not None:
            if not isinstance(data['assignee_ids'], list):
                errors.append("assignee_ids must be an array")
        
        return errors
    
    def validate_update(self, data: Dict) -> List[str]:
        """Valide les données de mise à jour d'une tâche"""
        errors = []
        
        if data.get('title') is not None:
            if len(data['title']) < 3:
                errors.append("Title must be at least 3 characters")
            elif len(data['title']) > 200:
                errors.append("Title must not exceed 200 characters")
        
        if data.get('status'):
            if data['status'] not in [s.value for s in TaskStatus]:
                errors.append(f"Invalid status. Must be one of: {', '.join([s.value for s in TaskStatus])}")
        
        if data.get('priority'):
            if data['priority'] not in [p.value for p in TaskPriority]:
                errors.append(f"Invalid priority. Must be one of: {', '.join([p.value for p in TaskPriority])}")
        
        if data.get('due_date'):
            try:
                datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except:
                errors.append("Invalid due_date format. Use ISO 8601 format")
        
        if data.get('estimated_hours') is not None:
            if not isinstance(data['estimated_hours'], (int, float)) or data['estimated_hours'] < 0:
                errors.append("Estimated hours must be a positive number")
        
        if data.get('assignee_ids') is not None:
            if not isinstance(data['assignee_ids'], list):
                errors.append("assignee_ids must be an array")
        
        return errors