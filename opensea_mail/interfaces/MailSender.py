import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailSender:
    def __init__(
        self, subject: str, body: str, sender_email: str, receiver_email: str, password: str
    ) -> None:
        self._subject = subject
        self._body = body
        self._sender_email = sender_email
        self._receiver_email = receiver_email
        self._password = password

    def send_email(self):
        message = MIMEMultipart()
        message["From"] = self._sender_email
        message["To"] = self._receiver_email
        message["Subject"] = self._subject

        # Attach the body to the email
        message.attach(MIMEText(self._body, "plain"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self._sender_email, self._password)
            server.sendmail(self._sender_email, self._receiver_email, message.as_string())