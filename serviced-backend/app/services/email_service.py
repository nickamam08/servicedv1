import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_welcome_email(email: str, full_name: str):
    """
    Sends a welcome email to the user.
    If SMTP is not configured, it logs the message instead.
    """
    subject = f"¡Bienvenido a SERVICED, {full_name}!"
    body = f"""
    Hola {full_name},
    
    ¡Gracias por unirte a SERVICED! Estamos muy contentos de tenerte con nosotros.
    
    Explora nuestra plataforma para encontrar los mejores servicios o para ofrecer los tuyos.
    
    Si tienes alguna pregunta, no dudes en contactarnos.
    
    Saludos,
    El equipo de SERVICED
    """

    # Check for SMTP configuration
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning(f"SMTP not configured. Welcome email to {email} logged instead.")
        print(f"\n--- [DEBUG EMAIL] TO: {email} ---")
        print(f"Subject: {subject}")
        print(f"Content: {body}")
        print("--- [END DEBUG EMAIL] ---\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Welcome email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending welcome email to {email}: {e}")

def send_password_reset_email(email: str, token: str):
    """
    Sends a password reset email to the user.
    """
    subject = "Restablece tu contraseña - SERVICED"
    # In a real app, this would be the actual URL. 
    # Since we are in dev, we assume it's relative to where it's served.
    reset_link = f"{settings.FRONTEND_HOST}/users/reset-password.html?token={token}"
    body = f"""
    Hola,
    
    Has solicitado restablecer tu contraseña en SERVICED. Haz clic en el siguiente enlace para continuar:
    
    {reset_link}
    
    Si no solicitaste este cambio, puedes ignorar este correo.
    
    Saludos,
    El equipo de SERVICED
    """

    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning(f"SMTP not configured. Password reset email to {email} logged instead.")
        print(f"\n--- [DEBUG EMAIL] TO: {email} ---")
        print(f"Subject: {subject}")
        print(f"Content: {body}")
        print("--- [END DEBUG EMAIL] ---\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {e}")
