import pytest
from src.auth.auth_utils import PermissionValidator
from src.constants import Role
from src.schemas.auth import CurrentUser


class TestPermissionValidator:
    @pytest.mark.parametrize(
        "user,permissions,expected",
        [
            (
                CurrentUser(
                    id=1,
                    email="teste@teste.com",
                    name="Test user",
                    role=[Role.CLIENT.value],
                    enabled=True,
                ),
                [Role.ADMIN],
                False,
            ),
            (
                CurrentUser(
                    id=1,
                    email="teste@teste.com",
                    name="Test user",
                    role=[Role.ADMIN.value],
                    enabled=True,
                ),
                [Role.ADMIN, Role.CURATOR, Role.CLIENT],
                True,
            ),
            (
                CurrentUser(
                    id=1,
                    email="teste@teste.com",
                    name="Test user",
                    role=[Role.CURATOR.value],
                    enabled=True,
                ),
                [Role.ADMIN, Role.CLIENT],
                False,
            ),
        ],
    )
    def test_permissions(
        self, user: CurrentUser, permissions: list[Role], expected: bool
    ) -> None:
        assert PermissionValidator(user, permissions)._verify_roles() is expected
