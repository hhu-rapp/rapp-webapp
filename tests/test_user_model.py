import pytest

from app.models import User


class TestUserModel():
    """A class containing tests for the user model."""

    def test_create_user(self):
        """Test if a user can be created."""
        user: User = User(
            email='test@email.com',
            password='password123'
        )   # type: ignore

        assert user.email == 'test@email.com'
        assert user.verify_password('password123')

    def test_password_setter(self):
        """Test if password can be written."""
        user: User = User(password='password123')   # type: ignore
        assert user.password_hashed is not None

    def test_password_getter(self):
        """Test if password can not be read."""
        user: User = User(password='password123')   # type: ignore
        with pytest.raises(AttributeError):
            user.password

    def test_verify_password(self):
        """Test password verification."""
        user: User = User(password='password123')   # type: ignore

        assert user.verify_password('password123')
        assert not user.verify_password('not_password')

    def test_user_save(self, app):
        """Test if user can be saved to the database."""
        email: str = 'user.save@test.de'

        with app.app_context():
            assert User.query.filter_by(id=0).first() is None

        user: User = User(
            email=email,
            password='saveuser'
        )    # type: ignore

        with app.app_context():
            user.save()
            assert User.query.filter_by(email=email).first() == user
