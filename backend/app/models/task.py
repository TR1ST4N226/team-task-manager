import enum
from app import db
from datetime import datetime

class TaskStatus(enum.Enum):
    TODO = 'TODO'  # Changé : majuscules
    IN_PROGRESS = 'IN_PROGRESS'  # Changé : majuscules
    REVIEW = 'REVIEW'  # Changé : majuscules
    DONE = 'DONE'  # Changé : majuscules

class TaskPriority(enum.Enum):
    LOW = 'LOW'  # Changé : majuscules
    MEDIUM = 'MEDIUM'  # Changé : majuscules
    HIGH = 'HIGH'  # Changé : majuscules
    URGENT = 'URGENT'  # Changé : majuscules

# Table d'association pour les assignés multiples
task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    estimated_hours = db.Column(db.Float, nullable=True)
    actual_hours = db.Column(db.Float, nullable=True)
    progress = db.Column(db.Integer, default=0)
    
    # Clés étrangères
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_tasks')
    assignees = db.relationship('User', secondary=task_assignees, back_populates='assigned_tasks', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='task', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', back_populates='task', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', back_populates='task', lazy='dynamic', cascade='all, delete-orphan')
    
    # Relation avec l'équipe
    team = db.relationship('Team', back_populates='tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'progress': self.progress,
            'creator': self.creator.to_dict() if self.creator else None,
            'creator_id': self.creator_id,
            'assignees': [user.to_dict() for user in self.assignees],
            'assignee_ids': [user.id for user in self.assignees],
            'team_id': self.team_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comment_count': self.comments.count(),
            'attachment_count': self.attachments.count()
        }
    
    def is_overdue(self):
        """Vérifie si la tâche est en retard"""
        if not self.due_date or self.status == TaskStatus.DONE:
            return False
        return datetime.utcnow() > self.due_date
    
    def is_completed(self):
        return self.status == TaskStatus.DONE
    
    def update_progress(self):
        """Met à jour le progrès en fonction du statut"""
        if self.status == TaskStatus.TODO:
            self.progress = 0
        elif self.status == TaskStatus.IN_PROGRESS:
            self.progress = max(self.progress, 25)
        elif self.status == TaskStatus.REVIEW:
            self.progress = max(self.progress, 75)
        elif self.status == TaskStatus.DONE:
            self.progress = 100
            self.completed_at = datetime.utcnow()