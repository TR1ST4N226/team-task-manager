from typing import List, Optional
from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)
    
    def find_by_user(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Trouve les notifications d'un utilisateur"""
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(read=False)
        return query.order_by(Notification.created_at.desc()).all()
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Marque une notification comme lue"""
        notification = self.find_by_id(notification_id)
        if notification:
            notification.read = True
            db.session.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Marque toutes les notifications d'un utilisateur comme lues"""
        notifications = Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).all()
        
        count = len(notifications)
        for notification in notifications:
            notification.read = True
        db.session.commit()
        return count
    
    def get_unread_count(self, user_id: int) -> int:
        """Compte les notifications non lues d'un utilisateur"""
        return Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).count()