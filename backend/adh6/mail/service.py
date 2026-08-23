"""SMTP sending, modelled on hosting's app/services/email.py which runs in production."""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from adh6.config.configuration import settings

logger = logging.getLogger(__name__)


def send_mail(
    *,
    to: str | list[str],
    subject: str,
    plain: str,
    html: str,
    bcc: list[str] | None = None,
) -> bool:
    """Send a mail. Never raises: returns False and logs a warning on failure.

    Never raising is deliberate: a delivery failure must not roll back a business transaction. A
    member who paid for a cable must not see the sale fail because the SMTP server is unreachable.
    Mails go out after the commit, and a failure is a warning in the logs.
    """
    recipients = [to] if isinstance(to, str) else list(to)
    # Filter empty addresses: an unset recipient variable would yield [""], a non-empty list, and
    # the empty address would travel all the way to SMTP.
    recipients = [address for address in recipients if address]
    all_recipients = recipients + [address for address in (bcc or []) if address]
    if not all_recipients:
        logger.warning("No recipient for the mail %r, not sending it", subject)
        return False

    if not settings.mail_enabled:
        logger.info("Mails disabled, not sending %r to %s", subject, ", ".join(all_recipients))
        return True

    if not settings.smtp_server:
        logger.warning("No SMTP server configured, not sending %r", subject)
        return False

    message = MIMEMultipart("alternative")
    message["From"] = settings.mail_from
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    # Plain part first: a mail client picks the last part it can render, so the HTML wins when it
    # is able to display it.
    message.attach(MIMEText(plain, "plain", "utf-8"))
    message.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(host=settings.smtp_server, port=settings.smtp_port) as smtp:
            smtp.sendmail(settings.mail_from, all_recipients, message.as_string())
    except (smtplib.SMTPException, OSError):
        logger.warning("Failed to send the mail %r to %s", subject, ", ".join(all_recipients), exc_info=True)
        return False

    logger.info("Mail %r sent to %s", subject, ", ".join(all_recipients))
    return True


async def send_mail_async(
    *,
    to: str | list[str],
    subject: str,
    plain: str,
    html: str,
    bcc: list[str] | None = None,
) -> bool:
    """Async wrapper around :func:`send_mail` -- runs SMTP in a thread.

    adh6 is fully async: a blocking smtplib call in the event loop would freeze every other
    request for the duration of the SMTP exchange.
    """
    return await asyncio.to_thread(send_mail, to=to, subject=subject, plain=plain, html=html, bcc=bcc)
