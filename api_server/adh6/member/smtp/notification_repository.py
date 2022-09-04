from adh6.default.decorator.log_call import log_call
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from adh6.member.interfaces.notification_repository import NotificationRepository

class NotificationSMTPRepository(NotificationRepository):
    def __init__(self):
        pass

    @log_call
    def send(self, ctx, recipient: str, subject: str, body: str):
        server = smtplib.SMTP('192.168.102.18', 25)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = "no-reply@minet.net"
        msg['To'] = Address("MiNET", recipient)
        msg.set_content(f"""\{ body }        """)
        server.send_message(msg)