from typing import List, Optional
from app.models.comment import Comment
from app.repositories.base_repository import BaseRepository

class CommentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Comment)
    
    def find_by_task(self, task_id: int) -> List[Comment]:
        """Trouve tous les commentaires d'une tâche"""
        return Comment.query.filter_by(task_id=task_id).order_by(
            Comment.created_at.desc()
        ).all()
    
    def find_replies(self, parent_id: int) -> List[Comment]:
        """Trouve toutes les réponses à un commentaire"""
        return Comment.query.filter_by(parent_id=parent_id).order_by(
            Comment.created_at.asc()
        ).all()
    
    def find_by_author(self, author_id: int) -> List[Comment]:
        """Trouve tous les commentaires d'un auteur"""
        return Comment.query.filter_by(author_id=author_id).order_by(
            Comment.created_at.desc()
        ).all()