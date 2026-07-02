from app import db
from datetime import datetime
import enum

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    memberships = db.relationship('TeamMembership', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='team', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo_url': self.logo_url,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': self.memberships.count(),
            'members': [membership.to_dict() for membership in self.memberships]
        }

class TeamMembership(db.Model):
    __tablename__ = 'team_memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, manager, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', back_populates='team_memberships')
    team = db.relationship('Team', back_populates='memberships')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'team_id', name='unique_user_team'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'team_id': self.team_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }