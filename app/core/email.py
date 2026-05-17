import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_email(to: str, subject: str, body: str) -> None:
    """Send an email via SMTP"""
    message = MIMEMultipart()
    message["From"] = settings.MAIL_FROM
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_HOST,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        start_tls=True
    )

async def send_reset_password_email(to: str, token: str) -> None:
    """Send a password reset email with the reset link"""
    reset_link = f"{settings.APP_URL}/reset-password?token={token}"
    body = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password. This link expires in 15 minutes.</p>
        <a href="{reset_link}">Reset Password</a>
        <p>If you didn't request this, ignore this email.</p>
    """

    await send_email(to, "Password Reset Request", body)
