from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.analytics_service import AnalyticsService
from app.services.export_service import ExportService
from app.services.team_service import TeamService
from io import BytesIO
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()
export_service = ExportService()
team_service = TeamService()

@analytics_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """
    Récupérer les statistiques du dashboard
    ---
    tags:
      - Analytics
    parameters:
      - name: team_id
        in: query
        type: integer
    responses:
      200:
        description: Statistiques du dashboard
      403:
        description: Accès refusé à l'équipe
    """
    user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    
    # Si team_id est spécifié, vérifier que l'utilisateur y a accès
    if team_id:
        teams = team_service.get_user_teams(user_id)
        if not any(t['id'] == team_id for t in teams):
            return jsonify({'error': 'You are not a member of this team'}), 403
    
    stats = analytics_service.get_dashboard_stats(team_id)
    return jsonify(stats), 200

@analytics_bp.route('/productivity-trends', methods=['GET'])
@jwt_required()
def get_productivity_trends():
    """
    Récupérer les tendances de productivité
    ---
    tags:
      - Analytics
    parameters:
      - name: team_id
        in: query
        type: integer
      - name: days
        in: query
        type: integer
        default: 30
    responses:
      200:
        description: Tendances de productivité
      403:
        description: Accès refusé
    """
    user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    if days > 90:
        return jsonify({'error': 'Maximum 90 days allowed'}), 400
    
    # Vérifier l'accès à l'équipe
    if team_id:
        teams = team_service.get_user_teams(user_id)
        if not any(t['id'] == team_id for t in teams):
            return jsonify({'error': 'You are not a member of this team'}), 403
    
    trends = analytics_service.get_productivity_trends(team_id, days)
    return jsonify(trends), 200

@analytics_bp.route('/team-performance/<int:team_id>', methods=['GET'])
@jwt_required()
def get_team_performance(team_id):
    """
    Récupérer la performance d'une équipe
    ---
    tags:
      - Analytics
    parameters:
      - name: team_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Performance de l'équipe
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
    
    performance = analytics_service.get_team_performance(team_id)
    
    if not performance:
        return jsonify({'error': 'Team not found'}), 404
    
    return jsonify(performance), 200

@analytics_bp.route('/user-performance', methods=['GET'])
@jwt_required()
def get_user_performance():
    """
    Récupérer la performance de l'utilisateur actuel
    ---
    tags:
      - Analytics
    parameters:
      - name: team_id
        in: query
        type: integer
    responses:
      200:
        description: Performance de l'utilisateur
    """
    user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    
    performance = analytics_service.get_user_performance(user_id, team_id)
    return jsonify(performance), 200

@analytics_bp.route('/user-performance/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_performance_by_id(user_id):
    """
    Récupérer la performance d'un utilisateur spécifique
    ---
    tags:
      - Analytics
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: team_id
        in: query
        type: integer
    responses:
      200:
        description: Performance de l'utilisateur
      403:
        description: Accès refusé
      404:
        description: Utilisateur non trouvé
    """
    current_user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    
    # Vérifier que l'utilisateur a accès (admin ou lui-même)
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    current_user = auth_service.user_repository.find_by_id(current_user_id)
    
    if current_user_id != user_id and current_user.role.value != 'admin':
        return jsonify({'error': 'You do not have permission to view this user\'s performance'}), 403
    
    performance = analytics_service.get_user_performance(user_id, team_id)
    
    if not performance:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(performance), 200

@analytics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    """
    Exporter les données (PDF, Excel, CSV)
    ---
    tags:
      - Analytics
    parameters:
      - name: team_id
        in: query
        type: integer
      - name: format
        in: query
        type: string
        enum: [pdf, excel, csv]
        default: pdf
      - name: team_name
        in: query
        type: string
    responses:
      200:
        description: Fichier exporté
      400:
        description: Format invalide
      403:
        description: Accès refusé
    """
    user_id = get_jwt_identity()
    team_id = request.args.get('team_id', type=int)
    export_format = request.args.get('format', 'pdf').lower()
    team_name = request.args.get('team_name', 'Team Report')
    
    # Vérifier l'accès à l'équipe
    if team_id:
        teams = team_service.get_user_teams(user_id)
        if not any(t['id'] == team_id for t in teams):
            return jsonify({'error': 'You are not a member of this team'}), 403
    
    # Récupérer les données
    data = analytics_service.get_export_data(team_id)
    
    # Exporter selon le format
    try:
        if export_format == 'pdf':
            file_data = export_service.export_to_pdf(data, team_name)
            filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            mimetype = 'application/pdf'
        elif export_format == 'excel':
            file_data = export_service.export_to_excel(data)
            filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif export_format == 'csv':
            file_data = export_service.export_to_csv(data)
            filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            mimetype = 'text/csv'
        else:
            return jsonify({'error': 'Invalid export format. Use pdf, excel, or csv'}), 400
        
        return send_file(
            BytesIO(file_data),
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500