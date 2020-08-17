# coding=utf-8
import requests
import requests.exceptions
from flask import current_app

from src.util.env import is_development_environment

ADH6_USER = "adh6_user"
ADH6_ADMIN = "adh6_admin"

TESTING_CLIENT = 'TestingClient'


def token_info(access_token) -> dict:

    if current_app.config["TESTING"]:
        return {
            "uid": TESTING_CLIENT,
            "scope": ["profile"],
            "groups": []
        }
    return authenticate_against_sso(access_token)


def get_sso_groups(token):
    try:
        verify_cert = True
        if is_development_environment():
            verify_cert = False

        headers = {"Authorization": "Bearer " + token}
        r = requests.get(
            current_app.config["AUTH_PROFILE_ADDRESS"],
            headers=headers,
            timeout=1,
            verify=verify_cert
        )
    except requests.exceptions.ReadTimeout:
        return None
    if r.status_code != 200 or "id" not in r.json():
        return None

    result = r.json()
    return result


def authenticate_against_sso(access_token):
    infos = get_sso_groups(access_token)
    if not infos:
        return None
    return {
        "uid": infos["id"],
        "scope": ['profile'],
    }
