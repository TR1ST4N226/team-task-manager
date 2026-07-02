from app import db
from datetime import datetime
import enum

class NotificationType(enum.Enum):
    TASK_ASSIGNED = 'task_assigned'
    TASK_UPDATED = 'task_updated'
    TASK_COMPLETED = 'task_completed'
    TASK_OVERDUE = 'task_overdue'
    COMMENT_ADDED = 'comment_added'
    MENTIONED = 'mentioned'
    TEAM_INVITE = 'team_invite'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Données supplémentaires
    read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', foreign_keys=[user_id], back_populates='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value if self.type else None,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }