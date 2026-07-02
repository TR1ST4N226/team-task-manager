import os
import uuid
from typing import Optional
import mimetypes

class FileUtils:
    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """Génère un nom de fichier unique"""
        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4().hex}{ext}"
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Récupère le MIME type d'un fichier"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Récupère la taille d'un fichier en octets"""
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    @staticmethod
    def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
        """Vérifie si le fichier a une extension autorisée"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_extensions
    
    @staticmethod
    def save_file(file, directory: str, filename: str) -> str:
        """Sauvegarde un fichier"""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        file.save(filepath)
        return filepath
    
    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Supprime un fichier"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except:
            return False
    
    @staticmethod
    def get_upload_folder() -> str:
        """Récupère le dossier d'upload"""
        return os.getenv('UPLOAD_FOLDER', 'uploads')