from typing import Optional, List, Dict
from datetime import datetime
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository
from app.models.notification import NotificationType
from app.interfaces.notification_sender import NotificationSender
from app.factories.notification_factory import NotificationFactory

class NotificationService:
    def __init__(self, senders: List[NotificationSender] = None):
        self.notification_repository = NotificationRepository()
        self.user_repository = UserRepository()
        self.task_repository = TaskRepository()
        self.senders = senders or []
    
    def send_task_assignment(self, task_id: int, assignee_id: int, assigner_id: int) -> bool:
        """Envoie une notification d'assignation de tâche"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return False
        
        assigner = self.user_repository.find_by_id(assigner_id)
        if not assigner:
            return False
        
        notification = NotificationFactory.create_task_assignment(
            task_id=task_id,
            assignee_id=assignee_id,
            assigner_id=assigner_id
        )
        
        return self._send_notification(notification)
    
    def send_task_update(self, task_id: int, user_id: int, update_data: Dict) -> bool:
        """Envoie une notification de mise à jour de tâche"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return False
        
        notification = NotificationFactory.create_task_update(
            task_id=task_id,
            user_id=user_id,
            update_data=update_data
        )
        
        return self._send_notification(notification)
    
    def send_team_invite(self, team_id: int, user_id: int, inviter_id: int) -> bool:
        """Envoie une invitation à rejoindre une équipe"""
        from app.repositories.team_repository import TeamRepository
        team_repo = TeamRepository()
        team = team_repo.find_by_id(team_id)
        if not team:
            return False
        
        notification = NotificationFactory.create_team_invite(
            team_id=team_id,
            user_id=user_id,
            inviter_id=inviter_id
        )
        
        return self._send_notification(notification)
    
    def send_comment_notification(self, task_id: int, user_id: int, comment_author_id: int) -> bool:
        """Envoie une notification de commentaire"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return False
        
        comment_author = self.user_repository.find_by_id(comment_author_id)
        if not comment_author:
            return False
        
        notification = NotificationFactory.create_comment_notification(
            task_id=task_id,
            user_id=user_id,
            comment_author_id=comment_author_id
        )
        
        return self._send_notification(notification)
    
    def send_overdue_notification(self, task_id: int, user_id: int) -> bool:
        """Envoie une notification de tâche en retard"""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return False
        
        notification = NotificationFactory.create_overdue_notification(
            task_id=task_id,
            user_id=user_id
        )
        
        return self._send_notification(notification)
    
    def _send_notification(self, notification) -> bool:
        """Envoie une notification via tous les canaux configurés"""
        # Sauvegarder la notification en base de données
        saved_notification = self.notification_repository.create({
            'user_id': notification.user_id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'data': notification.data,
            'read': False,
            'email_sent': False
        })
        
        # Envoyer via les canaux configurés
        for sender in self.senders:
            try:
                sender.send(saved_notification)
            except Exception as e:
                print(f"Error sending notification via {sender.__class__.__name__}: {e}")
        
        return True
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Récupère les notifications d'un utilisateur"""
        notifications = self.notification_repository.find_by_user(user_id, unread_only)
        return [n.to_dict() for n in notifications]
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Marque une notification comme lue"""
        notification = self.notification_repository.find_by_id(notification_id)
        if not notification:
            return False, "Notification not found"
        
        if notification.user_id != user_id:
            return False, "You don't have permission to read this notification"
        
        return self.notification_repository.mark_as_read(notification_id), None
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Marque toutes les notifications d'un utilisateur comme lues"""
        return self.notification_repository.mark_all_as_read(user_id)
    
    def get_unread_count(self, user_id: int) -> int:
        """Récupère le nombre de notifications non lues"""
        return self.notification_repository.get_unread_count(user_id)