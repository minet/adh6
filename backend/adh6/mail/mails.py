"""One function per mail adh6 sends.

Subjects live here rather than in the templates: a subject is not part of the rendered body, and
keeping them together makes it obvious that every mail has exactly one entry per language.
"""

import logging
from datetime import date, datetime

from .service import send_mail_async
from .templates import normalize_language, render

logger = logging.getLogger(__name__)

# One subject per language. No bilingual entry: a mail is sent in ONE language.
SUBJECTS = {
    "welcome": {
        "fr": "Bienvenue chez MiNET",
        "en": "Welcome to MiNET",
    },
    "receipt": {
        "fr": "Reçu de cotisation MiNET",
        "en": "MiNET membership receipt",
    },
    # A single entry on purpose: mails to the treasury list stay in French. They go to MiNET
    # volunteers, not to a member, so there is no preference to honour.
    "purchase_admin": {
        "fr": "Nouvel achat de matériel",
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


async def send_subscription_receipt_async(
    *,
    to: str,
    first_name: str,
    username: str,
    price: str,
    months: int,
    end_date: date | None,
    payment_method: str,
    paid_at: date,
    language: str | None = None,
) -> bool:
    """Receipt for a subscription recorded at the office desk.

    Members who pay online get a receipt from payment; members who pay in cash at the desk used to
    get nothing at all -- even though cash is precisely the case where they have no bank statement
    to prove anything. Same template as payment's, only the payment method differs.
    """
    language = normalize_language(language)
    context = {
        "prenom": first_name,
        "username": username,
        "prix": price,
        "nbr_mois": months,
        "date_fin": end_date,
        "payment_method": payment_method,
        "paid_at": paid_at,
    }
    return await send_mail_async(
        to=to,
        subject=SUBJECTS["receipt"][language],
        plain=render("receipt_subscription.txt.j2", language=language, **context),
        html=render("receipt_subscription.html.j2", language=language, **context),
    )


async def send_purchase_admin_async(
    *,
    to: list[str],
    username: str,
    adh6_url: str,
    items: list[dict[str, object]],
    total: str,
    payment_method: str,
    author: str,
    paid_at: datetime,
) -> bool:
    """Tells the treasury list that hardware was sold, so stock and cash can be followed.

    French only, and identified by username plus the ADH6 link rather than by email address: this
    goes to a mailing list whose archives are kept without a time limit and readable by every
    subscriber, present and future. The link gives the same information behind authentication.
    """
    context = {
        "username": username,
        "adh6_url": adh6_url,
        "items": items,
        "total": total,
        "payment_method": payment_method,
        "author": author,
        "paid_at": paid_at,
    }
    return await send_mail_async(
        to=to,
        subject=SUBJECTS["purchase_admin"]["fr"],
        plain=render("purchase_admin.txt.j2", language="fr", **context),
        html=render("purchase_admin.html.j2", language="fr", **context),
    )
