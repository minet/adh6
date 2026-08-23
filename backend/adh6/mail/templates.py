"""Jinja environment shared by every mail sent from adh6."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from adh6.config.configuration import settings

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# StrictUndefined is deliberate: a forgotten variable raises at render time -- so during tests --
# instead of leaving a silent hole in a mail already on its way to a member.
jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=True,
    undefined=StrictUndefined,
)

# Month names handed to the templates: strftime("%B") would depend on the container locale, which
# is English in the python-alpine image.
jinja_env.globals["MONTHS_FR"] = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]
jinja_env.globals["MONTHS_EN"] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

SUPPORTED_LANGUAGES = ("fr", "en")


def normalize_language(language: str | None) -> str:
    """Bring any input back to a supported language.

    The value comes from the member record, but an unexpected one must not produce an empty mail:
    every template branches on `lang`, so an unknown value would match no branch at all.
    """
    if language in SUPPORTED_LANGUAGES:
        return str(language)
    if settings.mail_default_language in SUPPORTED_LANGUAGES:
        return settings.mail_default_language
    return "fr"


def render(name: str, language: str | None = None, **context: object) -> str:
    """Render a mail template, injecting the context every mail shares."""
    return jinja_env.get_template(name).render(
        logo_url=settings.mail_logo_url,
        lang=normalize_language(language),
        **context,
    )
