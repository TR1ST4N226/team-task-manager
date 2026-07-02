from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.team_service import TeamService
from app.services.user_service import UserService
from app.validators.team_validator import TeamValidator

team_bp = Blueprint('team', __name__)
team_service = TeamService()
user_service = UserService()
team_validator = TeamValidator()

@team_bp.route('', methods=['GET'])
@jwt_required()
def get_teams():
    """
    Récupérer toutes les équipes de l'utilisateur
    ---
    tags:
      - Teams
    responses:
      200:
        description: Liste des équipes
    """
    user_id = get_jwt_identity()
    teams = team_service.get_user_teams(user_id)
    return jsonify(teams), 200

@team_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """
    Créer une nouvelle équipe
    ---
    tags:
      - Teams
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            name:
              type: string
              required: true
            description:
              type: string
            logo_url:
              type: string
    responses:
      201:
        description: Équipe créée avec succès
      400:
        description: Erreur de validation
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = team_validator.validate_create(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    data['created_by'] = user_id
    team, error = team_service.create_team(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Team created successfully',
        'team': team
    }), 201

@team_bp.route('/<int:team_id>', methods=['GET'])
@jwt_required()
def get_team(team_id):
    """
    Récupérer les détails d'une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Détails de l'équipe
      403:
        description: Accès refusé
      404:
        description: Équipe non trouvée
    """
    user_id = get_jwt_identity()
    
    # Vérifier que l'utilisateur est membre de l'équipe
    teams = team_service.get_user_teams(user_id)
    if not any(t['id'] == team_id for t in teams):
        return jsonify({'error': 'You are not a member of this team'}), 403
    
    team = team_service.get_team(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    return jsonify(team), 200

@team_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """
    Mettre à jour une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            name:
              type: string
            description:
              type: string
            logo_url:
              type: string
    responses:
      200:
        description: Équipe mise à jour
      403:
        description: Permission refusée
      404:
        description: Équipe non trouvée
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    team, error = team_service.update_team(team_id, data, user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Team updated successfully',
        'team': team
    }), 200

@team_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """
    Supprimer une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Équipe supprimée
      403:
        description: Permission refusée
      404:
        description: Équipe non trouvée
    """
    user_id = get_jwt_identity()
    
    success, error = team_service.delete_team(team_id, user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return '', 204

@team_bp.route('/<int:team_id>/members', methods=['GET'])
@jwt_required()
def get_team_members(team_id):
    """
    Récupérer les membres d'une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Liste des membres
      403:
        description: Accès refusé
      404:
        description: Équipe non trouvée
    """
    user_id = get_jwt_identity()
    
    # Vérifier que l'utilisateur est membre
    teams = team_service.get_user_teams(user_id)
    if not any(t['id'] == team_id for t in teams):
        return jsonify({'error': 'You are not a member of this team'}), 403
    
    team = team_service.get_team(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    members = team.get('members', [])
    return jsonify(members), 200

@team_bp.route('/<int:team_id>/members', methods=['POST'])
@jwt_required()
def add_team_member(team_id):
    """
    Ajouter un membre à une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_id:
              type: integer
              required: true
            role:
              type: string
              enum: [admin, manager, member]
              default: member
    responses:
      200:
        description: Membre ajouté
      400:
        description: Erreur de validation
      403:
        description: Permission refusée
      404:
        description: Équipe non trouvée
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({'error': 'user_id is required'}), 400
    
    role = data.get('role', 'member')
    success, error = team_service.add_member(team_id, data['user_id'], role, current_user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower() or "already" in error.lower():
            return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Member added successfully'}), 200

@team_bp.route('/<int:team_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_team_member(team_id, user_id):
    """
    Retirer un membre d'une équipe
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Membre retiré
      403:
        description: Permission refusée
      404:
        description: Équipe non trouvée
    """
    current_user_id = get_jwt_identity()
    
    success, error = team_service.remove_member(team_id, user_id, current_user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Member removed successfully'}), 200

@team_bp.route('/<int:team_id>/members/<int:user_id>/role', methods=['PATCH'])
@jwt_required()
def update_member_role(team_id, user_id):
    """
    Mettre à jour le rôle d'un membre
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            role:
              type: string
              enum: [admin, manager, member]
              required: true
    responses:
      200:
        description: Rôle mis à jour
      400:
        description: Erreur de validation
      403:
        description: Permission refusée
      404:
        description: Équipe non trouvée
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('role'):
        return jsonify({'error': 'role is required'}), 400
    
    success, error = team_service.update_member_role(team_id, user_id, data['role'], current_user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Role updated successfully'}), 200