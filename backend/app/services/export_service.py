from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import json

class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def export_to_excel(self, data: Dict) -> bytes:
        """Exporte les données au format Excel"""
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        # Feuille des tâches
        if data.get('tasks'):
            tasks_df = pd.DataFrame(data['tasks'])
            # Nettoyer les données pour Excel
            for col in ['assignees', 'creator', 'comments']:
                if col in tasks_df.columns:
                    tasks_df[col] = tasks_df[col].apply(lambda x: str(x) if x else '')
            tasks_df.to_excel(writer, sheet_name='Tasks', index=False)
        
        # Feuille des membres
        if data.get('members'):
            members_df = pd.DataFrame(data['members'])
            members_df.to_excel(writer, sheet_name='Members', index=False)
        
        # Feuille des statistiques
        if data.get('statistics'):
            stats_df = pd.DataFrame([data['statistics']])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        writer.close()
        return output.getvalue()
    
    def export_to_pdf(self, data: Dict, team_name: str = None) -> bytes:
        """Exporte les données au format PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563EB'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        title_text = f"Task Report - {team_name or 'All Teams'}"
        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 12))
        
        # Date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 12))
        
        # Statistiques
        if data.get('statistics'):
            elements.append(Paragraph("Statistics", self.styles['Heading2']))
            stats = data['statistics']
            stats_data = [
                ['Metric', 'Value'],
                ['Total Tasks', str(stats.get('total', 0))],
                ['Completed', str(stats.get('completed', 0))],
                ['In Progress', str(stats.get('in_progress', 0))],
                ['Overdue', str(stats.get('overdue', 0))],
                ['Completion Rate', f"{stats.get('completion_rate', 0)}%"]
            ]
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 20))
        
        # Tâches
        if data.get('tasks'):
            elements.append(Paragraph("Tasks", self.styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            tasks = data['tasks'][:20]  # Limiter à 20 pour le PDF
            task_data = [['ID', 'Title', 'Status', 'Priority', 'Assignee', 'Due Date']]
            
            for task in tasks:
                assignees = ', '.join([a.get('username', '') for a in task.get('assignees', [])])
                due_date = task.get('due_date', '')
                if due_date:
                    try:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    except:
                        pass
                
                task_data.append([
                    str(task.get('id', '')),
                    task.get('title', '')[:30] + ('...' if len(task.get('title', '')) > 30 else ''),
                    task.get('status', ''),
                    task.get('priority', ''),
                    assignees,
                    due_date
                ])
            
            task_table = Table(task_data)
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elements.append(task_table)
            
            if len(data['tasks']) > 20:
                elements.append(Spacer(1, 10))
                note_style = ParagraphStyle(
                    'NoteStyle',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=TA_LEFT
                )
                elements.append(Paragraph(f"* Showing first 20 of {len(data['tasks'])} tasks", note_style))
        
        # Générer le PDF
        doc.build(elements)
        return buffer.getvalue()
    
    def export_to_csv(self, data: Dict) -> bytes:
        """Exporte les données au format CSV"""
        output = io.StringIO()
        
        if data.get('tasks'):
            tasks_df = pd.DataFrame(data['tasks'])
            tasks_df.to_csv(output, index=False)
        
        return output.getvalue().encode('utf-8')