from typing import Optional, Dict, List, Tuple
from datetime import datetime
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.services.activity_service import ActivityService

class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository()
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()
        self.notification_service = NotificationService()
        self.activity_service = ActivityService()
    
    def add_comment(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Ajoute un commentaire à une tâche"""
        if not data.get('content'):
            return None, "Comment content is required"
        
        if not data.get('task_id'):
            return None, "Task ID is required"
        
        if not data.get('author_id'):
            return None, "Author ID is required"
        
        # Vérifier que la tâche existe
        task = self.task_repository.find_by_id(data['task_id'])
        if not task:
            return None, "Task not found"
        
        # Vérifier que l'auteur existe
        author = self.user_repository.find_by_id(data['author_id'])
        if not author:
            return None, "Author not found"
        
        # Vérifier le parent si spécifié
        parent_id = data.get('parent_id')
        if parent_id:
            parent = self.comment_repository.find_by_id(parent_id)
            if not parent:
                return None, "Parent comment not found"
            if parent.task_id != data['task_id']:
                return None, "Parent comment does not belong to this task"
        
        # Créer le commentaire
        comment = self.comment_repository.create({
            'content': data['content'],
            'task_id': data['task_id'],
            'author_id': data['author_id'],
            'parent_id': parent_id
        })
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=data['author_id'],
            task_id=data['task_id'],
            action='comment_added',
            details={'comment_id': comment.id, 'is_reply': parent_id is not None}
        )
        
        # Notifier les assignés de la tâche (sauf l'auteur)
        for assignee in task.assignees:
            if assignee.id != data['author_id']:
                self.notification_service.send_comment_notification(
                    task_id=data['task_id'],
                    user_id=assignee.id,
                    comment_author_id=data['author_id']
                )
        
        return comment.to_dict(), None
    
    def update_comment(self, comment_id: int, content: str, user_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        """Met à jour un commentaire"""
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None, "Comment not found"
        
        # Vérifier que l'utilisateur est l'auteur du commentaire
        if comment.author_id != user_id:
            return None, "You don't have permission to edit this comment"
        
        # Mettre à jour
        comment = self.comment_repository.update(comment_id, {'content': content})
        
        self.activity_service.log_activity(
            user_id=user_id,
            task_id=comment.task_id,
            action='comment_updated',
            details={'comment_id': comment_id}
        )
        
        return comment.to_dict(), None
    
    def delete_comment(self, comment_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Supprime un commentaire"""
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            return False, "Comment not found"
        
        # Vérifier que l'utilisateur est l'auteur ou admin de l'équipe
        # TODO: Vérifier les permissions avancées
        
        # Supprimer toutes les réponses
        replies = self.comment_repository.find_replies(comment_id)
        for reply in replies:
            self.comment_repository.delete(reply.id)
        
        self.activity_service.log_activity(
            user_id=user_id,
            task_id=comment.task_id,
            action='comment_deleted',
            details={'comment_id': comment_id}
        )
        
        return self.comment_repository.delete(comment_id), None
    
    def get_task_comments(self, task_id: int) -> List[Dict]:
        """Récupère tous les commentaires d'une tâche"""
        comments = self.comment_repository.find_by_task(task_id)
        return [comment.to_dict() for comment in comments]
    
    def get_comment_with_replies(self, comment_id: int) -> Optional[Dict]:
        """Récupère un commentaire avec toutes ses réponses"""
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            return None
        
        return comment.to_dict()