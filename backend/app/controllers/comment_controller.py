from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_service import CommentService
from app.services.task_service import TaskService
from app.validators.comment_validator import CommentValidator

comment_bp = Blueprint('comments', __name__)
comment_service = CommentService()
task_service = TaskService()
comment_validator = CommentValidator()

@comment_bp.route('/task/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task_comments(task_id):
    """
    Récupérer tous les commentaires d'une tâche
    ---
    tags:
      - Comments
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Liste des commentaires
      404:
        description: Tâche non trouvée
    """
    # Vérifier que la tâche existe
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    comments = comment_service.get_task_comments(task_id)
    return jsonify(comments), 200

@comment_bp.route('', methods=['POST'])
@jwt_required()
def add_comment():
    """
    Ajouter un commentaire à une tâche
    ---
    tags:
      - Comments
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            task_id:
              type: integer
              required: true
            content:
              type: string
              required: true
            parent_id:
              type: integer
    responses:
      201:
        description: Commentaire ajouté
      400:
        description: Erreur de validation
      404:
        description: Tâche non trouvée
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    errors = comment_validator.validate_create(data)
    if errors:
        return jsonify({'errors': errors}), 422
    
    data['author_id'] = user_id
    comment, error = comment_service.add_comment(data)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Comment added successfully',
        'comment': comment
    }), 201

@comment_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """
    Mettre à jour un commentaire
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            content:
              type: string
              required: true
    responses:
      200:
        description: Commentaire mis à jour
      400:
        description: Erreur de validation
      403:
        description: Permission refusée
      404:
        description: Commentaire non trouvé
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    comment, error = comment_service.update_comment(comment_id, data['content'], user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Comment updated successfully',
        'comment': comment
    }), 200

@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """
    Supprimer un commentaire
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Commentaire supprimé
      403:
        description: Permission refusée
      404:
        description: Commentaire non trouvé
    """
    user_id = get_jwt_identity()
    
    success, error = comment_service.delete_comment(comment_id, user_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({'error': error}), 404
        if "permission" in error.lower():
            return jsonify({'error': error}), 403
        return jsonify({'error': error}), 400
    
    return '', 204

@comment_bp.route('/<int:comment_id>/replies', methods=['GET'])
@jwt_required()
def get_comment_replies(comment_id):
    """
    Récupérer les réponses d'un commentaire
    ---
    tags:
      - Comments
    parameters:
      - name: comment_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Liste des réponses
      404:
        description: Commentaire non trouvé
    """
    comment = comment_service.get_comment_with_replies(comment_id)
    
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    return jsonify(comment.get('replies', [])), 200