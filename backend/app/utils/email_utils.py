import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List

class EmailUtils:
    def __init__(self):
        self.host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.port = int(os.getenv('SMTP_PORT', 587))
        self.user = os.getenv('SMTP_USER')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM', self.user)
    
    def send_email(self, to: List[str], subject: str, body: str, 
                   html: Optional[str] = None) -> bool:
        """Envoie un email"""
        if not self.user or not self.password:
            print("SMTP credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to)
            
            # Version texte
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)
            
            # Version HTML
            if html:
                part2 = MIMEText(html, 'html')
                msg.attach(part2)
            
            # Envoyer l'email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_task_assignment_email(self, to_email: str, task_title: str, 
                                   assigner_name: str, task_url: str) -> bool:
        """Envoie un email d'assignation de tâche"""
        subject = f"New Task Assigned: {task_title}"
        body = f"""
        Hello,
        
        You have been assigned a new task: {task_title}
        Assigned by: {assigner_name}
        
        View the task here: {task_url}
        
        Regards,
        Team Task Manager
        """
        html = f"""
        <h2>New Task Assigned</h2>
        <p>You have been assigned a new task: <strong>{task_title}</strong></p>
        <p>Assigned by: {assigner_name}</p>
        <p><a href="{task_url}">View Task</a></p>
        <br>
        <p>Regards,<br>Team Task Manager</p>
        """
        return self.send_email([to_email], subject, body, html)
    
    def send_team_invite_email(self, to_email: str, team_name: str, 
                               inviter_name: str, invite_url: str) -> bool:
        """Envoie un email d'invitation à une équipe"""
        subject = f"Team Invitation: {team_name}"
        body = f"""
        Hello,
        
        You have been invited to join the team: {team_name}
        Invited by: {inviter_name}
        
        Accept the invitation here: {invite_url}
        
        Regards,
        Team Task Manager
        """
        html = f"""
        <h2>Team Invitation</h2>
        <p>You have been invited to join: <strong>{team_name}</strong></p>
        <p>Invited by: {inviter_name}</p>
        <p><a href="{invite_url}">Accept Invitation</a></p>
        <br>
        <p>Regards,<br>Team Task Manager</p>
        """
        return self.send_email([to_email], subject, body, html)
    
    def send_password_reset_email(self, to_email: str, reset_url: str) -> bool:
        """Envoie un email de réinitialisation de mot de passe"""
        subject = "Password Reset Request"
        body = f"""
        Hello,
        
        You have requested to reset your password.
        
        Click the link below to reset your password:
        {reset_url}
        
        If you didn't request this, ignore this email.
        
        Regards,
        Team Task Manager
        """
        html = f"""
        <h2>Password Reset</h2>
        <p>You have requested to reset your password.</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <br>
        <p>If you didn't request this, ignore this email.</p>
        <br>
        <p>Regards,<br>Team Task Manager</p>
        """
        return self.send_email([to_email], subject, body, html)