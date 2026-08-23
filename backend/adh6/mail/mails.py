"""One function per mail adh6 sends.

Subjects live here rather than in the templates: a subject is not part of the rendered body, and
keeping them together makes it obvious that every mail has exactly one entry per language.
"""

import logging

from .service import send_mail_async
from .templates import normalize_language, render

logger = logging.getLogger(__name__)

# One subject per language. No bilingual entry: a mail is sent in ONE language.
SUBJECTS = {
    "welcome": {
        "fr": "Bienvenue chez MiNET",
        "en": "Welcome to MiNET",
    },
}


async def send_welcome_async(
    *,
    to: str,
    first_name: str,
    username: str,
    has_subscription: bool,
    language: str | None = None,
) -> bool:
    """Sent right after a member is created at the office desk.

    `has_subscription` drives both the wording and the call to action: a member registered at the
    desk has not necessarily paid yet, so the mail points to payment.minet.net instead of the
    device portal.
    """
    language = normalize_language(language)
    context = {"prenom": first_name, "username": username, "a_cotise": has_subscription}
    return await send_mail_async(
        to=to,
        subject=SUBJECTS["welcome"][language],
        plain=render("welcome.txt.j2", language=language, **context),
        html=render("welcome.html.j2", language=language, **context),
    )
