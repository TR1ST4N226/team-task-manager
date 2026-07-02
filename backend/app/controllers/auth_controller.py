from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.validators.auth_validator import AuthValidator
import re

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
user_service = UserService()
auth_validator = AuthValidator()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
              example: user@example.com
            username:
              type: string
              example: johndoe
            password:
              type: string
              example: Password123!
            full_name:
              type: string
              example: John Doe
    responses:
      201:
        description: Utilisateur créé avec succès
      400:
        description: Erreur de validation
      409:
        description: Email ou username déjà utilisé
    """
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = auth_validator.validate_register(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    # Inscription
    user, error = auth_service.register(
        email=data['email'],
        username=data['username'],
        password=data['password'],
        full_name=data.get('full_name')
    )
    
    if error:
        if "already" in error.lower():
            return jsonify({'error': error}), 409
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: Password123!
    responses:
      200:
        description: Connexion réussie
      401:
        description: Identifiants invalides
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = auth_validator.validate_login(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    # Connexion
    result, error = auth_service.login(
        email=data['email'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify(result), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Rafraîchir le token d'accès
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Nouveau token généré
      401:
        description: Token invalide
    """
    user_id = get_jwt_identity()
    
    access_token, error = auth_service.refresh_token(user_id)
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Déconnexion (invalide le token côté client)
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Déconnexion réussie
    """
    # Le client doit supprimer le token
    # Le serveur ne garde pas d'état, donc pas d'action spécifique
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Changer le mot de passe
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            old_password:
              type: string
              example: OldPassword123!
            new_password:
              type: string
              example: NewPassword123!
    responses:
      200:
        description: Mot de passe changé avec succès
      400:
        description: Erreur de validation
      401:
        description: Ancien mot de passe incorrect
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = auth_validator.validate_password_change(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    success, error = auth_service.change_password(
        user_id=user_id,
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    if error:
        if "incorrect" in error.lower():
            return jsonify({'error': error}), 401
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Password changed successfully'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Réinitialiser le mot de passe (envoie un email)
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
              example: user@example.com
    responses:
      200:
        description: Email de réinitialisation envoyé
      404:
        description: Email non trouvé
    """
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    success, error = auth_service.reset_password(data['email'])
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Password reset email sent'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Récupérer l'utilisateur actuel
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Informations de l'utilisateur
      404:
        description: Utilisateur non trouvé
    """
    user_id = get_jwt_identity()
    user = user_service.get_user_profile(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user), 200