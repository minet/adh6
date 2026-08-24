"""Render every mail template.

The Jinja environment uses StrictUndefined, so a template that renders proves the documented
context is enough, and one that raises proves a variable was forgotten. Without these tests the
strictness is worthless: nothing would ever render a template before a member receives it.
"""

import datetime as dt
import re

import pytest
from adh6.mail import render
from adh6.mail.mails import SUBJECTS

WELCOME = {"prenom": "Camille", "username": "camille.dupont", "a_cotise": False}
RECEIPT = {
    "prenom": "Camille",
    "username": "camille.dupont",
    "prix": "50.00",
    "nbr_mois": 12,
    "date_fin": dt.date(2027, 8, 24),
    "payment_method": "Espèces",
    "paid_at": dt.date(2026, 8, 24),
}
PURCHASE_ADMIN = {
    "username": "camille.dupont",
    "adh6_url": "https://adh6.minet.net/fr/member/view/1234/payment",
    "items": [{"name": "Câble Ethernet 3m", "price": "3.00", "stock_after": 12}],
    "total": "3.00",
    "payment_method": "Espèces",
    "author": "tim.cormier",
    "paid_at": dt.datetime(2026, 8, 24, 18, 42),
}

SUBSCRIPTION_ADMIN = {
    "username": "camille.dupont",
    "adh6_url": "https://adh6.minet.net/fr/member/view/1234/payment",
    "prix": "50.00",
    "nbr_mois": 12,
    "date_fin": dt.date(2027, 8, 24),
    "payment_method": "Espèces",
    "author": "tim.cormier",
    "paid_at": dt.datetime(2026, 8, 24, 18, 42),
}

ALL_TEMPLATES = [
    ("welcome.html.j2", WELCOME),
    ("welcome.txt.j2", WELCOME),
    ("receipt_subscription.html.j2", RECEIPT),
    ("receipt_subscription.txt.j2", RECEIPT),
    ("purchase_admin.html.j2", PURCHASE_ADMIN),
    ("purchase_admin.txt.j2", PURCHASE_ADMIN),
    ("admin_new_subscription.html.j2", SUBSCRIPTION_ADMIN),
    ("admin_new_subscription.txt.j2", SUBSCRIPTION_ADMIN),
]


@pytest.mark.parametrize(("template", "context"), ALL_TEMPLATES)
@pytest.mark.parametrize("language", ["fr", "en"])
def test_every_template_renders(template, context, language):
    assert len(render(template, language=language, **context)) > 200


@pytest.mark.parametrize(
    ("template", "context", "fr_marker", "en_marker"),
    [
        ("welcome.txt.j2", WELCOME, "Toute l'équipe", "The whole team"),
        ("receipt_subscription.txt.j2", RECEIPT, "Nous avons bien reçu", "We have received"),
    ],
)
def test_a_member_mail_carries_exactly_one_language(template, context, fr_marker, en_marker):
    """A mail is sent in ONE language. No context may produce both blocks."""
    fr = render(template, language="fr", **context)
    assert fr_marker in fr
    assert en_marker not in fr

    en = render(template, language="en", **context)
    assert en_marker in en
    assert fr_marker not in en


@pytest.mark.parametrize("language", [None, "", "de", "EN", "zh"])
def test_an_unknown_language_falls_back_instead_of_emptying_the_mail(language):
    """Without a fallback an unexpected value would satisfy no branch and produce an empty mail."""
    html = render("welcome.html.j2", language=language, **WELCOME)
    assert "Bienvenue chez MiNET" in html
    assert "Welcome to MiNET" not in html


def test_the_html_lang_attribute_follows_the_language():
    assert '<html lang="fr">' in render("welcome.html.j2", language="fr", **WELCOME)
    assert '<html lang="en">' in render("welcome.html.j2", language="en", **WELCOME)


def test_the_welcome_call_to_action_depends_on_the_subscription():
    """A member registered at the desk has not paid yet: send them to payment, not to the portal."""
    unpaid = render("welcome.html.j2", language="fr", **{**WELCOME, "a_cotise": False})
    assert "payment.minet.net" in unpaid

    paid = render("welcome.html.j2", language="fr", **{**WELCOME, "a_cotise": True})
    assert "minet.net/fr/services/" in paid


def test_no_data_uri_logo():
    """Gmail does not render `data:` images: the logo must stay a URL."""
    assert "data:image" not in render("welcome.html.j2", language="fr", **WELCOME)


def test_the_admin_mails_carry_no_email_address():
    """They go to a mailing list whose archives are kept without a time limit."""
    for template in ("purchase_admin.txt.j2", "purchase_admin.html.j2"):
        rendered = render(template, language="fr", **PURCHASE_ADMIN)
        # Not a plain `"@" not in`: the base stylesheet contains `@media` rules.
        assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", rendered)


def test_subjects_have_one_entry_per_language_and_no_bilingual_one():
    for key, subjects in SUBJECTS.items():
        for language, subject in subjects.items():
            assert "/" not in subject, f"{key}/{language} still looks bilingual"


@pytest.mark.parametrize("template", ["admin_new_subscription.txt.j2", "admin_new_subscription.html.j2"])
def test_the_subscription_admin_mail_carries_no_email_address(template):
    rendered = render(template, language="fr", **SUBSCRIPTION_ADMIN)
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", rendered)


def test_the_subscription_admin_mail_flags_a_missing_departure_date():
    """For the treasury, a missing date is an anomaly: it has to show."""
    text = render("admin_new_subscription.txt.j2", language="fr", **{**SUBSCRIPTION_ADMIN, "date_fin": None})
    assert "date de départ non lue" in text
