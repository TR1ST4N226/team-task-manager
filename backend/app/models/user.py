from app import db
from datetime import datetime
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    MEMBER = 'member'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    # Tâches créées par l'utilisateur
    created_tasks = db.relationship('Task', foreign_keys='Task.creator_id', back_populates='creator', lazy='dynamic')
    
    # Tâches assignées à l'utilisateur
    assigned_tasks = db.relationship('Task', secondary='task_assignees', back_populates='assignees', lazy='dynamic')
    
    # Commentaires
    comments = db.relationship('Comment', back_populates='author', lazy='dynamic')
    
    # Appartenance aux équipes
    team_memberships = db.relationship('TeamMembership', back_populates='user', lazy='dynamic')
    
    # Notifications
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', back_populates='user', lazy='dynamic')
    
    # Activités
    activities = db.relationship('ActivityLog', foreign_keys='ActivityLog.user_id', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'role': self.role.value if self.role else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def has_role(self, role):
        """Vérifie si l'utilisateur a un certain rôle ou plus"""
        if isinstance(role, str):
            role = UserRole(role)
        if self.role == UserRole.ADMIN:
            return True
        if self.role == UserRole.MANAGER and role in [UserRole.MANAGER, UserRole.MEMBER]:
            return True
        return self.role == role