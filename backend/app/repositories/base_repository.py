from typing import Optional, List, Dict, Any
from app import db

class BaseRepository:
    """Repository de base avec des opérations CRUD communes"""
    
    def __init__(self, model):
        self.model = model
    
    def create(self, data: Dict[str, Any]) -> Any:
        """Crée une nouvelle entité"""
        entity = self.model(**data)
        db.session.add(entity)
        db.session.commit()
        db.session.refresh(entity)
        return entity
    
    def find_by_id(self, id: int) -> Optional[Any]:
        """Trouve une entité par son ID"""
        return self.model.query.get(id)
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Récupère toutes les entités avec pagination"""
        return self.model.query.offset(skip).limit(limit).all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Any]:
        """Met à jour une entité"""
        entity = self.find_by_id(id)
        if entity:
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            db.session.commit()
            db.session.refresh(entity)
        return entity
    
    def delete(self, id: int) -> bool:
        """Supprime une entité"""
        entity = self.find_by_id(id)
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return True
        return False
    
    def count(self, filters: Dict = None) -> int:
        """Compte le nombre d'entités"""
        query = self.model.query
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        return query.count()