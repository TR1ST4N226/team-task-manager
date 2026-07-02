from typing import Optional, Dict, List, Tuple
from datetime import datetime
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.services.activity_service import ActivityService
from app import db

class TeamService:
    def __init__(self):
        self.team_repository = TeamRepository()
        self.user_repository = UserRepository()
        self.notification_service = NotificationService()
        self.activity_service = ActivityService()
    
    def create_team(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Crée une nouvelle équipe"""
        if not data.get('name'):
            return None, "Team name is required"
        
        if not data.get('created_by'):
            return None, "Creator ID is required"
        
        # Vérifier que le créateur existe
        creator = self.user_repository.find_by_id(data['created_by'])
        if not creator:
            return None, "Creator not found"
        
        # Créer l'équipe
        team = self.team_repository.create({
            'name': data['name'],
            'description': data.get('description', ''),
            'logo_url': data.get('logo_url'),
            'created_by': data['created_by']
        })
        
        # Ajouter le créateur comme admin
        self.team_repository.add_member(team.id, data['created_by'], 'admin')
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=data['created_by'],
            action='team_created',
            details={'team_name': team.name, 'team_id': team.id}
        )
        
        return team.to_dict(), None
    
    def update_team(self, team_id: int, data: Dict, user_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        """Met à jour une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return None, "Team not found"
        
        # Vérifier les permissions (admin de l'équipe ou admin système)
        if not self._is_team_admin(team_id, user_id):
            return None, "You don't have permission to update this team"
        
        allowed_fields = ['name', 'description', 'logo_url']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            team = self.team_repository.update(team_id, update_data)
            
            # Log de l'activité
            self.activity_service.log_activity(
                user_id=user_id,
                action='team_updated',
                details={'team_id': team_id, 'updates': update_data}
            )
        
        return team.to_dict(), None
    
    def delete_team(self, team_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Supprime une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return False, "Team not found"
        
        # Vérifier les permissions
        if not self._is_team_admin(team_id, user_id):
            return False, "You don't have permission to delete this team"
        
        # Log de l'activité
        self.activity_service.log_activity(
            user_id=user_id,
            action='team_deleted',
            details={'team_name': team.name, 'team_id': team_id}
        )
        
        return self.team_repository.delete(team_id), None
    
    def add_member(self, team_id: int, user_id: int, role: str = 'member', inviter_id: int = None) -> Tuple[bool, Optional[str]]:
        """Ajoute un membre à une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return False, "Team not found"
        
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Vérifier si l'utilisateur est déjà membre
        existing_members = team.memberships.filter_by(user_id=user_id).first()
        if existing_members:
            return False, "User is already a member of this team"
        
        # Ajouter le membre
        membership = self.team_repository.add_member(team_id, user_id, role)
        
        # Log de l'activité
        if inviter_id:
            self.activity_service.log_activity(
                user_id=inviter_id,
                action='team_member_added',
                details={'team_id': team_id, 'user_id': user_id, 'role': role}
            )
        
        # Notification
        self.notification_service.send_team_invite(
            team_id=team_id,
            user_id=user_id,
            inviter_id=inviter_id
        )
        
        return True, None
    
    def remove_member(self, team_id: int, user_id: int, remover_id: int) -> Tuple[bool, Optional[str]]:
        """Retire un membre d'une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return False, "Team not found"
        
        # Vérifier que le membre existe
        membership = team.memberships.filter_by(user_id=user_id).first()
        if not membership:
            return False, "User is not a member of this team"
        
        # Vérifier les permissions
        if not self._is_team_admin(team_id, remover_id) and remover_id != user_id:
            return False, "You don't have permission to remove this member"
        
        # Ne pas permettre de retirer le dernier admin
        admins = team.memberships.filter_by(role='admin').count()
        if membership.role == 'admin' and admins == 1 and remover_id != user_id:
            return False, "Cannot remove the last admin of the team"
        
        # Retirer le membre
        result = self.team_repository.remove_member(team_id, user_id)
        
        if result:
            self.activity_service.log_activity(
                user_id=remover_id,
                action='team_member_removed',
                details={'team_id': team_id, 'user_id': user_id}
            )
        
        return result, None
    
    def update_member_role(self, team_id: int, user_id: int, new_role: str, updater_id: int) -> Tuple[bool, Optional[str]]:
        """Met à jour le rôle d'un membre dans une équipe"""
        team = self.team_repository.find_by_id(team_id)
        if not team:
            return False, "Team not found"
        
        # Vérifier les permissions
        if not self._is_team_admin(team_id, updater_id):
            return False, "You don't have permission to update roles"
        
        # Vérifier que le membre existe
        membership = team.memberships.filter_by(user_id=user_id).first()
        if not membership:
            return False, "User is not a member of this team"
        
        # Ne pas permettre de changer le rôle d'un admin si c'est le dernier
        if membership.role == 'admin' and new_role != 'admin':
            admins = team.memberships.filter_by(role='admin').count()
            if admins == 1:
                return False, "Cannot change the role of the last admin"
        
        result = self.team_repository.update_member_role(team_id, user_id, new_role)
        
        if result:
            self.activity_service.log_activity(
                user_id=updater_id,
                action='team_member_role_updated',
                details={'team_id': team_id, 'user_id': user_id, 'new_role': new_role}
            )
        
        return result, None
    
    def get_team(self, team_id: int) -> Optional[Dict]:
        """Récupère les détails d'une équipe"""
        team = self.team_repository.find_by_id(team_id)
        return team.to_dict() if team else None
    
    def get_user_teams(self, user_id: int) -> List[Dict]:
        """Récupère toutes les équipes d'un utilisateur"""
        teams = self.team_repository.find_by_member(user_id)
        return [team.to_dict() for team in teams]
    
    def _is_team_admin(self, team_id: int, user_id: int) -> bool:
        """Vérifie si un utilisateur est admin d'une équipe"""
        membership = self.team_repository.find_by_id(team_id)
        if not membership:
            return False
        
        # Vérifier dans les membres
        team = self.team_repository.find_by_id(team_id)
        membership = team.memberships.filter_by(user_id=user_id).first()
        return membership and membership.role == 'admin'