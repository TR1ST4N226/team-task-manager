from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.team_repository import TeamRepository
from app.models.task import TaskStatus
from sqlalchemy import func, and_
from app import db

class AnalyticsService:
    def __init__(self):
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()
        self.team_repository = TeamRepository()
    
    def get_dashboard_stats(self, team_id: Optional[int] = None) -> Dict:
        """Récupère les statistiques pour le dashboard"""
        stats = self.task_repository.get_task_statistics(team_id)
        
        # Statistiques supplémentaires
        if team_id:
            team = self.team_repository.find_by_id(team_id)
            stats['team_members'] = team.memberships.count() if team else 0
        else:
            # CORRECTION: Utiliser len() au lieu de .count()
            users = self.user_repository.find_all(limit=1000)
            stats['team_members'] = len(users)
        
        # Tâches créées cette semaine
        week_ago = datetime.utcnow() - timedelta(days=7)
        from app.models.task import Task
        new_tasks = Task.query.filter(
            Task.created_at >= week_ago
        )
        if team_id:
            new_tasks = new_tasks.filter_by(team_id=team_id)
        stats['new_tasks_this_week'] = new_tasks.count()
        
        # Tâches terminées cette semaine
        completed_tasks = Task.query.filter(
            Task.status == TaskStatus.DONE,
            Task.completed_at >= week_ago
        )
        if team_id:
            completed_tasks = completed_tasks.filter_by(team_id=team_id)
        stats['completed_this_week'] = completed_tasks.count()
        
        return stats
    
    def get_productivity_trends(self, team_id: Optional[int] = None, 
                                days: int = 30) -> List[Dict]:
        """Récupère les tendances de productivité"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        from app.models.task import Task
        query = Task.query.filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date
        )
        if team_id:
            query = query.filter_by(team_id=team_id)
        
        # Grouper par jour
        daily_stats = query.with_entities(
            func.date(Task.created_at).label('date'),
            func.count(Task.id).label('created'),
            func.sum(func.cast(Task.status == TaskStatus.DONE, db.Integer)).label('completed')
        ).group_by(func.date(Task.created_at)).all()
        
        return [
            {
                'date': stat.date.isoformat(),
                'created': stat.created,
                'completed': stat.completed or 0
            }
            for stat in daily_stats
        ]
    
    def get_team_performance(self, team_id: int) -> Dict:
        """Récupère la performance d'une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return {}
        
        members = team.memberships.all()
        member_performance = []
        
        for membership in members:
            user = membership.user
            assigned_tasks = user.assigned_tasks.filter_by(team_id=team_id).all()
            completed_tasks = [t for t in assigned_tasks if t.is_completed()]
            
            member_performance.append({
                'user_id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'total_tasks': len(assigned_tasks),
                'completed_tasks': len(completed_tasks),
                'completion_rate': (len(completed_tasks) / len(assigned_tasks) * 100) if assigned_tasks else 0,
                'avg_completion_time': self._calculate_avg_completion_time(completed_tasks)
            })
        
        # Statistiques globales de l'équipe
        all_tasks = self.task_repository.find_with_filters({'team_id': team_id})
        completed = [t for t in all_tasks if t.is_completed()]
        
        return {
            'team_name': team.name,
            'total_members': len(members),
            'total_tasks': len(all_tasks),
            'completed_tasks': len(completed),
            'completion_rate': (len(completed) / len(all_tasks) * 100) if all_tasks else 0,
            'member_performance': member_performance
        }
    
    def get_user_performance(self, user_id: int, team_id: Optional[int] = None) -> Dict:
        """Récupère la performance d'un utilisateur"""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return {}
        
        # Tâches assignées
        tasks_query = user.assigned_tasks
        if team_id:
            tasks_query = tasks_query.filter_by(team_id=team_id)
        assigned_tasks = tasks_query.all()
        
        completed_tasks = [t for t in assigned_tasks if t.is_completed()]
        overdue_tasks = [t for t in assigned_tasks if t.is_overdue()]
        
        # Statistiques par priorité
        priority_stats = {}
        for task in assigned_tasks:
            priority = task.priority.value if task.priority else 'unknown'
            if priority not in priority_stats:
                priority_stats[priority] = {'total': 0, 'completed': 0}
            priority_stats[priority]['total'] += 1
            if task.is_completed():
                priority_stats[priority]['completed'] += 1
        
        return {
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'total_tasks': len(assigned_tasks),
            'completed_tasks': len(completed_tasks),
            'overdue_tasks': len(overdue_tasks),
            'completion_rate': (len(completed_tasks) / len(assigned_tasks) * 100) if assigned_tasks else 0,
            'avg_completion_time': self._calculate_avg_completion_time(completed_tasks),
            'priority_stats': priority_stats,
            'tasks_by_status': self._get_tasks_by_status(assigned_tasks)
        }
    
    def _calculate_avg_completion_time(self, tasks: List) -> Optional[float]:
        """Calcule le temps moyen de complétion en heures"""
        if not tasks:
            return None
        
        total_hours = 0
        count = 0
        
        for task in tasks:
            if task.completed_at and task.created_at:
                delta = task.completed_at - task.created_at
                total_hours += delta.total_seconds() / 3600
                count += 1
        
        return total_hours / count if count > 0 else None
    
    def _get_tasks_by_status(self, tasks: List) -> Dict:
        """Groupe les tâches par statut"""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = 0
        
        for task in tasks:
            status = task.status.value if task.status else 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def get_export_data(self, team_id: Optional[int] = None) -> Dict:
        """Récupère toutes les données pour l'export"""
        data = {
            'tasks': [],
            'members': [],
            'statistics': {}
        }
        
        # Récupérer les tâches
        filters = {}
        if team_id:
            filters['team_id'] = team_id
        tasks = self.task_repository.find_with_filters(filters)
        data['tasks'] = [task.to_dict() for task in tasks]
        
        # Récupérer les membres
        if team_id:
            team = self.team_repository.find_by_id(team_id)
            if team:
                members = team.memberships.all()
                data['members'] = [
                    {
                        'user': membership.user.to_dict(),
                        'role': membership.role,
                        'joined_at': membership.joined_at.isoformat() if membership.joined_at else None
                    }
                    for membership in members
                ]
        
        # Statistiques
        data['statistics'] = self.get_dashboard_stats(team_id)
        
        return data