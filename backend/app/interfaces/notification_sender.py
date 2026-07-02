from abc import ABC, abstractmethod
from app.models.notification import Notification

class NotificationSender(ABC):
    """Interface pour l'envoi de notifications"""
    
    @abstractmethod
    def send(self, notification: Notification) -> bool:
        """Envoie une notification"""
        pass
    
    @abstractmethod
    def supports(self, notification_type: str) -> bool:
        """Vérifie si le sender supporte ce type de notification"""
        pass