from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from .models import db, User, OAuth2Client
from .oauth2 import authorization, require_oauth
# from authlib.specs.rfc6749 import OAuth2Error
from website.ldap import LdapServ
from website.models import OAuth2Token


bp = Blueprint(__name__, 'home')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        if not user.check_password(password):
            return redirect('/')

        session['id'] = user.id
        return redirect('/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)


@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    # if request.method == 'GET':
    #     try:
    #         grant = authorization.validate_consent_request(end_user=user)
    #     except OAuth2Error as error:
    #         return error.error
    #     return render_template('authorize.html', user=user, grant=grant)
    # if not user and 'username' in request.form:
    #     username = request.form.get('username')
    #     user = User.query.filter_by(username=username).first()
    # if request.form['confirm']:
    if not user:
        return redirect('/')
    grant_user = user
    # else:
    #     grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)

#
# @bp.route('/oauth/token', methods=['POST'])
# def issue_token():
#     print(request.form)
#     return authorization.create_token_response()
#
#
# @bp.route('/oauth/revoke', methods=['POST'])
# def revoke_token():
#     return authorization.create_endpoint_response('revocation')
#


@bp.route('/api/groups/<token>')
def get_groups(token):

    passwd = request.args.get('passwd')
    if passwd != "VseVCqoW9WWpYdtwjKdGPUZhphccq7xAWgTg8ksDmZ":
        return "Unauthorized. Go away.", 401

    q = db.session.query(OAuth2Token)
    q = q.filter(OAuth2Token.access_token == token)
    tokenObj = q.one_or_none()
    if not tokenObj:
        return "[]"

    groups = LdapServ.find_groups(tokenObj.user.username)
    adh6_groups = []

    if "adh5" in groups:
        adh6_groups += ["adh6_user"]

    if "sudovpn" in groups:
        adh6_groups += ["adh6_admin"]

    return jsonify({
        "uid": tokenObj.user.username,
        "scopes": adh6_groups
    })


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)
