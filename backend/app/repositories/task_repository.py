from typing import Optional, List, Dict, Any
from app.models.task import Task, TaskStatus, TaskPriority
from app.repositories.base_repository import BaseRepository
from app import db
from datetime import datetime

class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Task)
    
    def find_with_filters(self, filters: Dict[str, Any]) -> List[Task]:
        """Trouve des tâches avec des filtres avancés"""
        query = Task.query
        
        # Filtres de base
        if filters.get('status'):
            query = query.filter(Task.status == filters['status'])
        
        if filters.get('priority'):
            query = query.filter(Task.priority == filters['priority'])
        
        if filters.get('assignee_id'):
            query = query.filter(Task.assignees.any(id=filters['assignee_id']))
        
        if filters.get('creator_id'):
            query = query.filter(Task.creator_id == filters['creator_id'])
        
        if filters.get('team_id'):
            query = query.filter(Task.team_id == filters['team_id'])
        
        # Recherche textuelle
        if filters.get('search'):
            search = f"%{filters['search']}%"
            query = query.filter(
                db.or_(
                    Task.title.ilike(search),
                    Task.description.ilike(search)
                )
            )
        
        # Filtre par date
        if filters.get('due_date_from'):
            query = query.filter(Task.due_date >= filters['due_date_from'])
        
        if filters.get('due_date_to'):
            query = query.filter(Task.due_date <= filters['due_date_to'])
        
        # Tâches en retard
        if filters.get('overdue'):
            query = query.filter(
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatus.DONE
            )
        
        # Tri
        sort_by = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'desc')
        
        if sort_order == 'desc':
            query = query.order_by(db.desc(getattr(Task, sort_by)))
        else:
            query = query.order_by(getattr(Task, sort_by))
        
        # Pagination
        if filters.get('limit'):
            query = query.limit(filters['limit'])
        
        if filters.get('offset'):
            query = query.offset(filters['offset'])
        
        return query.all()
    
    def get_tasks_by_assignee(self, user_id: int) -> List[Task]:
        """Récupère toutes les tâches assignées à un utilisateur"""
        return Task.query.filter(Task.assignees.any(id=user_id)).all()
    
    def get_tasks_by_creator(self, user_id: int) -> List[Task]:
        """Récupère toutes les tâches créées par un utilisateur"""
        return Task.query.filter_by(creator_id=user_id).all()
    
    def get_overdue_tasks(self) -> List[Task]:
        """Récupère toutes les tâches en retard"""
        return Task.query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != TaskStatus.DONE
        ).all()
    
    def get_task_statistics(self, team_id: Optional[int] = None) -> Dict:
        """Récupère les statistiques des tâches"""
        query = Task.query
        if team_id:
            query = query.filter_by(team_id=team_id)
        
        total = query.count()
        completed = query.filter_by(status=TaskStatus.DONE).count()
        in_progress = query.filter_by(status=TaskStatus.IN_PROGRESS).count()
        todo = query.filter_by(status=TaskStatus.TODO).count()
        review = query.filter_by(status=TaskStatus.REVIEW).count()
        overdue = query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != TaskStatus.DONE
        ).count()
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'todo': todo,
            'review': review,
            'overdue': overdue,
            'completion_rate': round(completion_rate, 2)
        }