import asyncio
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def main() -> None:
    message = EmailMessage()
    message["Subject"] = "Library SMTP Test"
    message["From"] = settings.email_from
    message["To"] = settings.email_from

    message.set_content(
        "This is a test email from the Library backend."
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=True,
    )

    print("Email sent to Mailtrap Sandbox.")


if __name__ == "__main__":
    asyncio.run(main())