
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_verification_email(
    recipient: str,
    token: str,
) -> None:
    message = EmailMessage()

    message["Subject"] = "Verify your Library account"
    message["From"] = settings.email_from
    message["To"] = recipient

    message.set_content(
        "Welcome to Library!\n\n"
        "Use the following token to verify your email:\n\n"
        f"{token}\n\n"
        "This token expires in 15 minutes."
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=True,
    )
