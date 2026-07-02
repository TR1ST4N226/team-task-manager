from typing import Optional, Dict, List
from datetime import datetime
from app.models.activity_log import ActivityLog
from app import db

class ActivityService:
    def log_activity(self, user_id: int, action: str, task_id: int = None, 
                     details: Dict = None, ip_address: str = None, 
                     user_agent: str = None) -> ActivityLog:
        """Journalise une activité"""
        activity = ActivityLog(
            user_id=user_id,
            task_id=task_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        db.session.refresh(activity)
        return activity
    
    def get_activities(self, user_id: int = None, task_id: int = None, 
                       limit: int = 50, offset: int = 0) -> List[Dict]:
        """Récupère les activités avec filtres"""
        query = ActivityLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if task_id:
            query = query.filter_by(task_id=task_id)
        
        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [activity.to_dict() for activity in activities]
    
    def get_task_activity(self, task_id: int, limit: int = 20) -> List[Dict]:
        """Récupère l'historique des activités d'une tâche"""
        return self.get_activities(task_id=task_id, limit=limit)
    
    def get_user_activity(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Récupère l'historique des activités d'un utilisateur"""
        return self.get_activities(user_id=user_id, limit=limit)