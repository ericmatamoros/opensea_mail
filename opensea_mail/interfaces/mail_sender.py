"""Email delivery over Gmail SMTP."""

import smtplib
from email.message import EmailMessage


class MailSender:
    def __init__(
        self,
        subject: str,
        body: str,
        sender_email: str,
        receiver_email: str,
        password: str,
        timeout: float = 30.0,
    ) -> None:
        missing = [
            name
            for name, value in (
                ("SENDER_EMAIL", sender_email),
                ("RECEIVER_EMAIL", receiver_email),
                ("SENDER_PASSWORD", password),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Missing email configuration: {', '.join(missing)}")

        self._subject = subject
        self._body = body
        self._sender_email = sender_email
        self._receiver_email = receiver_email
        self._password = password
        self._timeout = timeout

    def send_email(self) -> None:
        message = EmailMessage()
        message["From"] = self._sender_email
        message["To"] = self._receiver_email
        message["Subject"] = self._subject
        message.set_content(self._body)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=self._timeout) as server:
            server.starttls()
            server.login(self._sender_email, self._password)
            server.send_message(message)
