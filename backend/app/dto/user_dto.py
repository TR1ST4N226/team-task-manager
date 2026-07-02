from typing import Optional

class UserCreateDTO:
    def __init__(self, data: dict):
        self.email = data.get('email')
        self.username = data.get('username')
        self.password = data.get('password')
        self.full_name = data.get('full_name')
    
    def to_dict(self) -> dict:
        return {
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'full_name': self.full_name
        }

class UserUpdateDTO:
    def __init__(self, data: dict):
        self.full_name = data.get('full_name')
        self.username = data.get('username')
        self.avatar_url = data.get('avatar_url')
    
    def to_dict(self) -> dict:
        return {
            'full_name': self.full_name,
            'username': self.username,
            'avatar_url': self.avatar_url
        }