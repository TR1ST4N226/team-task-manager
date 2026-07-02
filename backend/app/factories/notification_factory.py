from typing import Dict
from app.models.notification import Notification, NotificationType
from datetime import datetime

class NotificationFactory:
    """Factory pour créer différents types de notifications"""
    
    @staticmethod
    def create_task_assignment(task_id: int, assignee_id: int, assigner_id: int) -> Notification:
        """Crée une notification d'assignation de tâche"""
        return Notification(
            user_id=assignee_id,
            type=NotificationType.TASK_ASSIGNED,
            title="New Task Assigned",
            message=f"You have been assigned a new task",
            data={
                'task_id': task_id,
                'assigner_id': assigner_id,
                'action': 'assigned'
            }
        )
    
    @staticmethod
    def create_task_update(task_id: int, user_id: int, update_data: Dict) -> Notification:
        """Crée une notification de mise à jour de tâche"""
        task_title = update_data.get('title', 'Task')
        return Notification(
            user_id=user_id,
            type=NotificationType.TASK_UPDATED,
            title="Task Updated",
            message=f"Task '{task_title}' has been updated",
            data={
                'task_id': task_id,
                'updates': update_data,
                'action': 'updated'
            }
        )
    
    @staticmethod
    def create_team_invite(team_id: int, user_id: int, inviter_id: int) -> Notification:
        """Crée une notification d'invitation à une équipe"""
        return Notification(
            user_id=user_id,
            type=NotificationType.TEAM_INVITE,
            title="Team Invitation",
            message=f"You have been invited to join a team",
            data={
                'team_id': team_id,
                'inviter_id': inviter_id,
                'action': 'invited'
            }
        )
    
    @staticmethod
    def create_comment_notification(task_id: int, user_id: int, comment_author_id: int) -> Notification:
        """Crée une notification de commentaire"""
        return Notification(
            user_id=user_id,
            type=NotificationType.COMMENT_ADDED,
            title="New Comment",
            message=f"Someone commented on a task you're assigned to",
            data={
                'task_id': task_id,
                'comment_author_id': comment_author_id,
                'action': 'commented'
            }
        )
    
    @staticmethod
    def create_overdue_notification(task_id: int, user_id: int) -> Notification:
        """Crée une notification de tâche en retard"""
        return Notification(
            user_id=user_id,
            type=NotificationType.TASK_OVERDUE,
            title="Task Overdue",
            message=f"A task assigned to you is overdue",
            data={
                'task_id': task_id,
                'action': 'overdue'
            }
        )