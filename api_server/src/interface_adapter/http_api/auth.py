# coding=utf-8
import requests
import requests.exceptions
from flask import current_app


USER = "adh6_user"
ADMIN = "adh6_admin"

TESTING_CLIENT = 'TestingClient'


def token_info(access_token) -> dict:

    if current_app.config["TESTING"]:
        return {
            "uid": TESTING_CLIENT,
            "scope": ["profile"],
            "groups": [
                "adh6_user", 
                "adh6_admin", 
                "adh6_treso",
                "adh6_superadmin",
                "cluster-dev",
                "cluster-prod",
                "cluster-hosting"
            ]
        }
    return authenticate_against_sso(access_token)


def get_sso_groups(token):
    try:
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(
            current_app.config["AUTH_PROFILE_ADDRESS"],
            headers=headers,
            timeout=1,
            verify=True
        )
    except requests.exceptions.ReadTimeout:
        return None
    if r.status_code != 200 or "id" not in r.json():
        return None

    result = r.json()
    print(result)
    return result


def authenticate_against_sso(access_token):
    infos = get_sso_groups(access_token)
    if not infos:
        return None
    groups = ['user']
    if 'attributes' in infos and 'memberOf' in infos['attributes']:
        groups += [e.split(",")[0].split("=")[1] for e in infos['attributes']['memberOf']]

    return {
        "uid": infos["id"],
        "scope": ['profile'],
        "groups": groups
    }
