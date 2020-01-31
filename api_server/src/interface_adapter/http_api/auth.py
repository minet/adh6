# coding=utf-8
import datetime
import requests
import requests.exceptions
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from src.interface_adapter.sql.model.database import Database as Db
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
    if is_development_environment():
        result["groups"] = [ADH6_USER, ADH6_ADMIN]  # If we are testing, consider the user asg.admin
    return result


def authenticate_against_sso(access_token):
    infos = get_sso_groups(access_token)
    if not infos:
        return None
    return {
        "uid": infos["id"],
        "scope": infos['scope'],
        "groups": infos["groups"]
    }
