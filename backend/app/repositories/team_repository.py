from typing import Optional, List
from app.models.team import Team, TeamMembership
from app.repositories.base_repository import BaseRepository
from app import db

class TeamRepository(BaseRepository):
    def __init__(self):
        super().__init__(Team)
    
    def find_by_member(self, user_id: int) -> List[Team]:
        """Trouve toutes les équipes dont un utilisateur est membre"""
        return Team.query.join(TeamMembership).filter(
            TeamMembership.user_id == user_id
        ).all()
    
    def add_member(self, team_id: int, user_id: int, role: str = 'member') -> TeamMembership:
        """Ajoute un membre à une équipe"""
        membership = TeamMembership(
            team_id=team_id,
            user_id=user_id,
            role=role
        )
        db.session.add(membership)
        db.session.commit()
        db.session.refresh(membership)
        return membership
    
    def remove_member(self, team_id: int, user_id: int) -> bool:
        """Retire un membre d'une équipe"""
        membership = TeamMembership.query.filter_by(
            team_id=team_id,
            user_id=user_id
        ).first()
        
        if membership:
            db.session.delete(membership)
            db.session.commit()
            return True
        return False
    
    def update_member_role(self, team_id: int, user_id: int, new_role: str) -> bool:
        """Met à jour le rôle d'un membre dans une équipe"""
        membership = TeamMembership.query.filter_by(
            team_id=team_id,
            user_id=user_id
        ).first()
        
        if membership:
            membership.role = new_role
            db.session.commit()
            return True
        return False
    
    def get_members(self, team_id: int) -> List[TeamMembership]:
        """Récupère tous les membres d'une équipe avec leurs rôles"""
        return TeamMembership.query.filter_by(team_id=team_id).all()