from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.validators.user_validator import UserValidator

user_bp = Blueprint('users', __name__)
user_service = UserService()
user_validator = UserValidator()

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Récupérer un utilisateur par ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Utilisateur trouvé
      404:
        description: Utilisateur non trouvé
    """
    user = user_service.get_user_profile(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Mettre à jour le profil de l'utilisateur actuel
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            full_name:
              type: string
              example: John Doe
            username:
              type: string
              example: johndoe
            avatar_url:
              type: string
              example: https://example.com/avatar.jpg
    responses:
      200:
        description: Profil mis à jour
      400:
        description: Erreur de validation
      404:
        description: Utilisateur non trouvé
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = user_validator.validate_profile_update(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    user, error = user_service.update_profile(user_id, data)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user
    }), 200

@user_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """
    Rechercher des utilisateurs
    ---
    tags:
      - Users
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Terme de recherche
      - name: limit
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Résultats de la recherche
    """
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400
    
    users = user_service.search_users(query, limit)
    return jsonify(users), 200

@user_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_user(user_id):
    """
    Désactiver un compte utilisateur (Admin seulement)
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Compte désactivé
      403:
        description: Permission refusée
      404:
        description: Utilisateur non trouvé
    """
    current_user_id = get_jwt_identity()
    
    # Vérifier les permissions (seul un admin peut désactiver)
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    current_user = auth_service.user_repository.find_by_id(current_user_id)
    
    if not current_user or current_user.role.value != 'admin':
        return jsonify({'error': 'Admin permission required'}), 403
    
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot deactivate yourself'}), 400
    
    success = user_service.deactivate_user(user_id)
    
    if not success:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'message': 'User deactivated successfully'}), 200

@user_bp.route('/<int:user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(user_id):
    """
    Activer un compte utilisateur (Admin seulement)
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Compte activé
      403:
        description: Permission refusée
      404:
        description: Utilisateur non trouvé
    """
    current_user_id = get_jwt_identity()
    
    # Vérifier les permissions
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    current_user = auth_service.user_repository.find_by_id(current_user_id)
    
    if not current_user or current_user.role.value != 'admin':
        return jsonify({'error': 'Admin permission required'}), 403
    
    success = user_service.activate_user(user_id)
    
    if not success:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'message': 'User activated successfully'}), 200