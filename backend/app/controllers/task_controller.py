from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.task_service import TaskService
from app.validators.task_validator import TaskValidator
from app.models.task import TaskStatus

task_bp = Blueprint('tasks', __name__)
task_service = TaskService()
task_validator = TaskValidator()

@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Récupérer la liste des tâches avec filtres
    ---
    tags:
      - Tasks
    parameters:
      - name: status
        in: query
        type: string
        enum: [todo, in-progress, review, done]
      - name: priority
        in: query
        type: string
        enum: [low, medium, high, urgent]
      - name: assignee_id
        in: query
        type: integer
      - name: team_id
        in: query
        type: integer
      - name: search
        in: query
        type: string
      - name: sort_by
        in: query
        type: string
        default: created_at
      - name: sort_order
        in: query
        type: string
        enum: [asc, desc]
        default: desc
      - name: limit
        in: query
        type: integer
        default: 100
      - name: offset
        in: query
        type: integer
        default: 0
    responses:
      200:
        description: Liste des tâches
    """
    user_id = get_jwt_identity()
    
    # Récupérer les filtres
    filters = {
        'status': request.args.get('status'),
        'priority': request.args.get('priority'),
        'assignee_id': request.args.get('assignee_id', type=int),
        'creator_id': request.args.get('creator_id', type=int),
        'team_id': request.args.get('team_id', type=int),
        'search': request.args.get('search'),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_order': request.args.get('sort_order', 'desc'),
        'limit': request.args.get('limit', 100, type=int),
        'offset': request.args.get('offset', 0, type=int),
        'overdue': request.args.get('overdue', type=bool)
    }
    
    # Si team_id est spécifié, vérifier que l'utilisateur y a accès
    if filters['team_id']:
        from app.services.team_service import TeamService
        team_service = TeamService()
        team = team_service.get_team(filters['team_id'])
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Vérifier que l'utilisateur est membre de l'équipe
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.find_by_id(user_id)
        if not any(t['id'] == filters['team_id'] for t in user_service.get_user_teams(user_id)):
            return jsonify({'error': 'You are not a member of this team'}), 403
    
    tasks = task_service.get_tasks(filters)
    return jsonify(tasks), 200

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """
    Récupérer une tâche par ID
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tâche trouvée
      404:
        description: Tâche non trouvée
    """
    task = task_service.get_task(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task), 200

@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """
    Créer une nouvelle tâche
    ---
    tags:
      - Tasks
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            title:
              type: string
              required: true
            description:
              type: string
            status:
              type: string
              enum: [todo, in-progress, review, done]
              default: todo
            priority:
              type: string
              enum: [low, medium, high, urgent]
              default: medium
            due_date:
              type: string
              format: date-time
            estimated_hours:
              type: number
            assignee_ids:
              type: array
              items:
                type: integer
            team_id:
              type: integer
    responses:
      201:
        description: Tâche créée avec succès
      400:
        description: Erreur de validation
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = task_validator.validate_create(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    # Ajouter le créateur
    data['creator_id'] = user_id
    
    task, error = task_service.create_task(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task
    }), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """
    Mettre à jour une tâche
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            title:
              type: string
            description:
              type: string
            priority:
              type: string
              enum: [low, medium, high, urgent]
            due_date:
              type: string
              format: date-time
            estimated_hours:
              type: number
            assignee_ids:
              type: array
              items:
                type: integer
            team_id:
              type: integer
    responses:
      200:
        description: Tâche mise à jour
      400:
        description: Erreur de validation
      404:
        description: Tâche non trouvée
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    task, error = task_service.update_task(task_id, data, user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Task updated successfully',
        'task': task
    }), 200

@task_bp.route('/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    """
    Mettre à jour le statut d'une tâche
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            status:
              type: string
              enum: [todo, in-progress, review, done]
              required: true
    responses:
      200:
        description: Statut mis à jour
      400:
        description: Erreur de validation
      404:
        description: Tâche non trouvée
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': 'Status is required'}), 400
    
    # Valider le statut
    if data['status'] not in [s.value for s in TaskStatus]:
        return jsonify({'error': 'Invalid status'}), 400
    
    task, error = task_service.update_task_status(task_id, data['status'], user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Task status updated successfully',
        'task': task
    }), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """
    Supprimer une tâche
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Tâche supprimée
      403:
        description: Permission refusée
      404:
        description: Tâche non trouvée
    """
    user_id = get_jwt_identity()
    
    # Vérifier les permissions (créateur ou admin)
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task['creator_id'] != user_id:
        # Vérifier si l'utilisateur est admin
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        current_user = auth_service.user_repository.find_by_id(user_id)
        if not current_user or current_user.role.value != 'admin':
            return jsonify({'error': 'You do not have permission to delete this task'}), 403
    
    success, error = task_service.delete_task(task_id, user_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return '', 204

@task_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_task_statistics():
    """
    Récupérer les statistiques des tâches
    ---
    tags:
      - Tasks
    parameters:
      - name: team_id
        in: query
        type: integer
    responses:
      200:
        description: Statistiques des tâches
    """
    user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    
    stats = task_service.get_task_statistics(team_id)
    return jsonify(stats), 200