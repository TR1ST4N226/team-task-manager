from typing import Optional, List, Dict
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app import db

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Trouve un utilisateur par email"""
        return User.query.filter_by(email=email).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Trouve un utilisateur par nom d'utilisateur"""
        return User.query.filter_by(username=username).first()
    
    def find_by_team(self, team_id: int) -> List[User]:
        """Trouve tous les membres d'une équipe"""
        from app.models.team import TeamMembership
        return User.query.join(TeamMembership).filter(
            TeamMembership.team_id == team_id
        ).all()
    
    def search(self, query: str, limit: int = 20) -> List[User]:
        """Recherche des utilisateurs par nom ou email"""
        search = f"%{query}%"
        return User.query.filter(
            db.or_(
                User.username.ilike(search),
                User.email.ilike(search),
                User.full_name.ilike(search)
            )
        ).limit(limit).all()
    
    def get_team_members_with_roles(self, team_id: int) -> List[Dict]:
        """Récupère les membres d'une équipe avec leurs rôles"""
        from app.models.team import TeamMembership
        results = db.session.query(
            User,
            TeamMembership.role
        ).join(
            TeamMembership,
            User.id == TeamMembership.user_id
        ).filter(
            TeamMembership.team_id == team_id
        ).all()
        
        return [{
            'user': user.to_dict(),
            'role': role
        } for user, role in results]