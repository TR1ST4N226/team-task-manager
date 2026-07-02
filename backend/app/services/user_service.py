from typing import Optional, Dict, List, Tuple
from app.repositories.user_repository import UserRepository
from app.repositories.team_repository import TeamRepository
from app import db

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.team_repository = TeamRepository()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Récupère un utilisateur par son ID"""
        user = self.user_repository.find_by_id(user_id)
        return user.to_dict() if user else None
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Récupère le profil complet d'un utilisateur avec ses statistiques"""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        
        profile = user.to_dict()
        
        # Statistiques de l'utilisateur
        from app.repositories.task_repository import TaskRepository
        task_repo = TaskRepository()
        
        assigned_tasks = task_repo.get_tasks_by_assignee(user_id)
        created_tasks = task_repo.get_tasks_by_creator(user_id)
        
        # CORRECTION: Utiliser len() au lieu de .count()
        teams = self.team_repository.find_by_member(user_id)
        
        profile['statistics'] = {
            'assigned_tasks_count': len(assigned_tasks),
            'created_tasks_count': len(created_tasks),
            'completed_tasks_count': sum(1 for t in assigned_tasks if t.is_completed()),
            'teams_count': len(teams)  # <-- CORRECTION ICI
        }
        
        return profile
    
    def update_profile(self, user_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """Met à jour le profil d'un utilisateur"""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Champs autorisés
        allowed_fields = ['full_name', 'username', 'avatar_url']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                if field == 'username':
                    # Vérifier si le username est déjà pris
                    existing = self.user_repository.find_by_username(data['username'])
                    if existing and existing.id != user_id:
                        return None, "Username already taken"
                update_data[field] = data[field]
        
        if update_data:
            user = self.user_repository.update(user_id, update_data)
        
        return user.to_dict(), None
    
    def search_users(self, query: str, limit: int = 20) -> List[Dict]:
        """Recherche des utilisateurs"""
        users = self.user_repository.search(query, limit)
        return [user.to_dict() for user in users]
    
    def get_team_members(self, team_id: int) -> List[Dict]:
        """Récupère les membres d'une équipe avec leurs rôles"""
        members = self.user_repository.get_team_members_with_roles(team_id)
        return members
    
    def deactivate_user(self, user_id: int) -> bool:
        """Désactive un compte utilisateur"""
        user = self.user_repository.find_by_id(user_id)
        if user:
            self.user_repository.update(user_id, {'is_active': False})
            return True
        return False
    
    def activate_user(self, user_id: int) -> bool:
        """Active un compte utilisateur"""
        user = self.user_repository.find_by_id(user_id)
        if user:
            self.user_repository.update(user_id, {'is_active': True})
            return True
        return False