from adh6.decorator import log_call
from adh6.misc import LOG
import smtplib
from flask import current_app
from email.message import EmailMessage
from email.headerregistry import Address

from ..interfaces import NotificationRepository


class NotificationSMTPRepository(NotificationRepository):
    @log_call
    def send(self, ctx, recipient: str, subject: str, body: str):
        smtp = current_app.config["SMTP_SERVER"]
        if not smtp:
            LOG.warning("No SMTP server defined, not sending emails")
            return
        server = smtplib.SMTP(smtp, 25)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = "no-reply@minet.net"
        msg['To'] = Address("MiNET", recipient)
        msg.set_content(f"""{ body }""")
        server.send_message(msg)