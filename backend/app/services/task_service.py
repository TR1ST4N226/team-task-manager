from typing import Optional, Dict, List, Tuple
from datetime import datetime
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.team_repository import TeamRepository
from app.services.notification_service import NotificationService
from app.services.activity_service import ActivityService
from app.models.task import TaskStatus, TaskPriority
from app import db

class TaskService:
    def __init__(self):
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()
        self.team_repository = TeamRepository()
        self.notification_service = NotificationService()
        self.activity_service = ActivityService()
    
    def create_task(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Crée une nouvelle tâche"""
        # Validation
        if not data.get('title'):
            return None, "Title is required"
        
        if not data.get('creator_id'):
            return None, "Creator ID is required"
        
        # Vérifier que le créateur existe
        creator = self.user_repository.find_by_id(data['creator_id'])
        if not creator:
            return None, "Creator not found"
        
        # Vérifier que les assignés existent
        assignee_ids = data.get('assignee_ids', [])
        assignees = []
        for user_id in assignee_ids:
            user = self.user_repository.find_by_id(user_id)
            if user:
                assignees.append(user)
        
        # Vérifier l'équipe si spécifiée
        team_id = data.get('team_id')
        if team_id:
            team = self.team_repository.find_by_id(team_id)
            if not team:
                return None, "Team not found"
        
        # Préparer les données de la tâche
        task_data = {
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', TaskStatus.TODO),
            'priority': data.get('priority', TaskPriority.MEDIUM),
            'due_date': data.get('due_date'),
            'estimated_hours': data.get('estimated_hours'),
            'creator_id': data['creator_id'],
            'team_id': team_id,
            'progress': 0
        }
        
        # Créer la tâche
        task = self.task_repository.create(task_data)
        
        # Ajouter les assignés
        if assignees:
            task.assignees.extend(assignees)
            db.session.commit()
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=data['creator_id'],
            task_id=task.id,
            action='task_created',
            details={'task_title': task.title, 'assignees': [u.id for u in assignees]}
        )
        
        # Envoyer des notifications aux assignés
        for assignee in assignees:
            self.notification_service.send_task_assignment(
                task_id=task.id,
                assignee_id=assignee.id,
                assigner_id=data['creator_id']
            )
        
        return task.to_dict(), None
    
    def update_task(self, task_id: int, data: Dict, user_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        """Met à jour une tâche"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return None, "Task not found"
        
        # Champs autorisés
        allowed_fields = ['title', 'description', 'priority', 'due_date', 'estimated_hours', 'team_id']
        update_data = {}
        
        # Tracker les changements pour les logs
        changes = {}
        
        for field in allowed_fields:
            if field in data:
                old_value = getattr(task, field)
                new_value = data[field]
                if old_value != new_value:
                    update_data[field] = new_value
                    changes[field] = {'old': old_value, 'new': new_value}
        
        # Mise à jour spéciale pour le statut
        if 'status' in data:
            old_status = task.status
            new_status = data['status']
            if old_status != new_status:
                update_data['status'] = new_status
                changes['status'] = {'old': old_status, 'new': new_status}
                
                # Si la tâche est terminée
                if new_status == TaskStatus.DONE:
                    update_data['completed_at'] = datetime.utcnow()
                    update_data['progress'] = 100
        
        # Mise à jour des assignés
        if 'assignee_ids' in data:
            old_assignees = set([u.id for u in task.assignees])
            new_assignees = set(data['assignee_ids'])
            
            # Ajouter les nouveaux assignés
            to_add = new_assignees - old_assignees
            for user_id_to_add in to_add:
                user = self.user_repository.find_by_id(user_id_to_add)
                if user:
                    task.assignees.append(user)
                    self.notification_service.send_task_assignment(
                        task_id=task.id,
                        assignee_id=user_id_to_add,
                        assigner_id=user_id
                    )
            
            # Retirer les anciens assignés
            to_remove = old_assignees - new_assignees
            for user_id_to_remove in to_remove:
                user = self.user_repository.find_by_id(user_id_to_remove)
                if user and user in task.assignees:
                    task.assignees.remove(user)
            
            changes['assignees'] = {
                'added': list(to_add),
                'removed': list(to_remove)
            }
        
        # Appliquer les mises à jour
        if update_data:
            task = self.task_repository.update(task_id, update_data)
        
        if changes:
            db.session.commit()
            db.session.refresh(task)
        
        # Log de l'activité
        if changes:
            self.activity_service.log_activity(
                user_id=user_id,
                task_id=task.id,
                action='task_updated',
                details=changes
            )
        
        return task.to_dict(), None
    
    def update_task_status(self, task_id: int, status: str, user_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        """Met à jour le statut d'une tâche"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return None, "Task not found"
        
        old_status = task.status
        new_status = TaskStatus(status)
        
        if old_status == new_status:
            return task.to_dict(), None
        
        update_data = {'status': new_status}
        if new_status == TaskStatus.DONE:
            update_data['completed_at'] = datetime.utcnow()
            update_data['progress'] = 100
        elif new_status == TaskStatus.IN_PROGRESS:
            update_data['progress'] = max(task.progress, 25)
        elif new_status == TaskStatus.REVIEW:
            update_data['progress'] = max(task.progress, 75)
        elif new_status == TaskStatus.TODO:
            update_data['completed_at'] = None
            update_data['progress'] = 0
        
        task = self.task_repository.update(task_id, update_data)
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=user_id,
            task_id=task.id,
            action='task_status_changed',
            details={'old_status': old_status.value, 'new_status': new_status.value}
        )
        
        # Notifier les assignés
        for assignee in task.assignees:
            if assignee.id != user_id:
                self.notification_service.send_task_update(
                    task_id=task.id,
                    user_id=assignee.id,
                    update_data={'status': new_status.value}
                )
        
        return task.to_dict(), None
    
    def delete_task(self, task_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Supprime une tâche"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return False, "Task not found"
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=user_id,
            task_id=task.id,
            action='task_deleted',
            details={'task_title': task.title}
        )
        
        return self.task_repository.delete(task_id), None
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Récupère une tâche avec tous ses détails"""
        task = self.task_repository.find_by_id(task_id)
        return task.to_dict() if task else None
    
    def get_tasks(self, filters: Dict) -> List[Dict]:
        """Récupère les tâches avec filtres"""
        tasks = self.task_repository.find_with_filters(filters)
        return [task.to_dict() for task in tasks]
    
    def get_task_statistics(self, team_id: Optional[int] = None) -> Dict:
        """Récupère les statistiques des tâches"""
        return self.task_repository.get_task_statistics(team_id)
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Récupère les tâches en retard"""
        tasks = self.task_repository.get_overdue_tasks()
        return [task.to_dict() for task in tasks]