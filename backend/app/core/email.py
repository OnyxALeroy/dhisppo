import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL]):
        print(f"[EMAIL] SMTP not configured. Would send to {to_email}: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL] Failed to send email: {e}")
        return False


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    subject = "Reset Your Dhisppo Password"
    
    text_body = f"""
Hi,

You requested a password reset for your Dhisppo account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The Dhisppo Team
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Reset Your Password</h2>
        <p>You requested a password reset for your Dhisppo account.</p>
        <p><a href="{reset_url}" class="button">Reset Password</a></p>
        <p>Or copy this link into your browser:</p>
        <p style="word-break: break-all;">{reset_url}</p>
        <p>This link will expire in 1 hour.</p>
        <div class="footer">
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>The Dhisppo Team</p>
        </div>
    </div>
</body>
</html>
"""

    return send_email(to_email, subject, html_body, text_body)
