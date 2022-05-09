import pytest
from src.use_case.decorator.security import HasRoleExpression, Roles, User, has_any_role, owns, OwnsExpression

@pytest.fixture
def sample_treso_user():
    yield User(1, "test", [Roles.TRESO.value])


@pytest.fixture
def sample_user_user():
    yield User(1, "test", [Roles.USER.value])


@pytest.fixture
def sample_admin_user():
    yield User(1, "test", [Roles.ADMIN.value])


def test_has_role_expression(sample_admin_user: User):
    assert HasRoleExpression(Roles.ADMIN)({"user": sample_admin_user}) is True


def test_has_not_role_expression(sample_user_user: User):
    assert HasRoleExpression(Roles.ADMIN)({"user": sample_user_user}) is False


def test_has_not_any_role_expression(sample_user_user: User):
    assert has_any_role([Roles.TRESO])({"user": sample_user_user}) is False


def test_has_any_role_expression(sample_user_user: User):
    assert has_any_role([Roles.TRESO, Roles.USER])({"user": sample_user_user}) is True
