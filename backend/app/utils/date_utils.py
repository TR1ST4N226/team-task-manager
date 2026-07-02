from datetime import datetime, timedelta
from typing import Optional

class DateUtils:
    @staticmethod
    def now() -> datetime:
        """Retourne la date actuelle en UTC"""
        return datetime.utcnow()
    
    @staticmethod
    def parse_iso(iso_string: str) -> Optional[datetime]:
        """Parse une chaîne ISO en datetime"""
        try:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def format_iso(dt: datetime) -> str:
        """Formate une datetime en ISO"""
        return dt.isoformat() if dt else None
    
    @staticmethod
    def days_between(date1: datetime, date2: datetime) -> int:
        """Calcule le nombre de jours entre deux dates"""
        delta = date2 - date1
        return delta.days
    
    @staticmethod
    def hours_between(date1: datetime, date2: datetime) -> float:
        """Calcule le nombre d'heures entre deux dates"""
        delta = date2 - date1
        return delta.total_seconds() / 3600
    
    @staticmethod
    def is_overdue(due_date: datetime) -> bool:
        """Vérifie si une date est dépassée"""
        if not due_date:
            return False
        return datetime.utcnow() > due_date
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Ajoute des jours à une date"""
        return dt + timedelta(days=days)
    
    @staticmethod
    def get_week_start(dt: datetime) -> datetime:
        """Retourne le début de la semaine (lundi)"""
        start = dt - timedelta(days=dt.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_month_start(dt: datetime) -> datetime:
        """Retourne le début du mois"""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)