from datetime import datetime
from typing import Optional, List
from app.models.task import TaskStatus, TaskPriority

class TaskCreateDTO:
    def __init__(self, data: dict):
        self.title = data.get('title')
        self.description = data.get('description', '')
        self.status = data.get('status', TaskStatus.TODO)
        self.priority = data.get('priority', TaskPriority.MEDIUM)
        self.due_date = data.get('due_date')
        self.estimated_hours = data.get('estimated_hours')
        self.creator_id = data.get('creator_id')
        self.team_id = data.get('team_id')
        self.assignee_ids = data.get('assignee_ids', [])
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_hours': self.estimated_hours,
            'creator_id': self.creator_id,
            'team_id': self.team_id,
            'assignee_ids': self.assignee_ids
        }

class TaskUpdateDTO:
    def __init__(self, data: dict):
        self.title = data.get('title')
        self.description = data.get('description')
        self.status = data.get('status')
        self.priority = data.get('priority')
        self.due_date = data.get('due_date')
        self.estimated_hours = data.get('estimated_hours')
        self.team_id = data.get('team_id')
        self.assignee_ids = data.get('assignee_ids')