import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str) -> None:
    """Send an email via SMTP. Raises on failure so Celery can retry."""
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning(
            "SMTP not configured. Skipping email to %s with subject: %s",
            to_email,
            subject,
        )
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

    logger.info("Email sent to %s: %s", to_email, subject)
