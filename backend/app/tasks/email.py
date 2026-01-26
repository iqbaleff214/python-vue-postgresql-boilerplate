import logging

from app.celery import celery_app
from app.mail.service import send_email
from app.mail.templates import reset_password_email

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.send_reset_password_email",
)
def send_reset_password_email(self, to_email: str, user_name: str, reset_link: str) -> None:
    """Send a password reset email. Retries up to 3 times on failure."""
    try:
        subject, html_body = reset_password_email(user_name, reset_link)
        send_email(to_email, subject, html_body)
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", to_email, exc)
        raise self.retry(exc=exc)
