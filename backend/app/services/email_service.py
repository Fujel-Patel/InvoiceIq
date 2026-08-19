from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def send_password_reset_email(email: str, reset_url: str) -> bool:
    """
    Send a password reset email.
    In production, integrate with Resend, SendGrid, or similar service.
    """
    logger.info(f"Password reset requested for {email}")
    logger.info(f"Reset URL: {reset_url}")

    # TODO: Implement actual email sending
    # Example with Resend:
    # import resend
    # resend.api_key = settings.RESEND_API_KEY
    # await resend.Emails.send({
    #     "from": "InvoiceIQ <noreply@yourdomain.com>",
    #     "to": email,
    #     "subject": "Reset your InvoiceIQ password",
    #     "html": f"<p>Click <a href='{reset_url}'>here</a> to reset your password.</p>",
    # })

    return True


async def send_verification_email(email: str, verification_url: str) -> bool:
    """Send an email verification email."""
    logger.info(f"Email verification requested for {email}")
    logger.info(f"Verification URL: {verification_url}")
    return True


async def send_welcome_email(email: str) -> bool:
    """Send a welcome email after signup."""
    logger.info(f"Welcome email for {email}")
    return True