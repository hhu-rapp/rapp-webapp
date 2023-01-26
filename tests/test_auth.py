from app.models import User


class TestAuth():
    def test_login(self, app):
        """Test Login"""
        email: str = 'login@test.com'
        password: str = 'password'
        user: User = User(
            email=email,
            password=password,
            confirmed=True
        )  # type: ignore

        with app.app_context():
            user.save()

        client = app.test_client()
        response = client.post(
            '/auth/login',
            data={
                'email': email,
                'password': password,
                'remember_me': False
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Eingeloggt als' in response.data

        response = client.get('/auth/login')
        assert response.status_code == 302

    def test_login_failed(self, app):
        """Test Login behaviour for wrong credentials."""
        email: str = 'failed_login@test.com'
        user: User = User(
            email=email,
            password='password',
            confirmed=True
        )  # type: ignore

        with app.app_context():
            user.save()

        client = app.test_client()
        response = client.post(
            '/auth/login',
            data={
                'email': email,
                'password': 'not_password',
                'remember_me': False
            }
        )
        assert response.status_code == 200
        assert b'Incorrect email or password.' in response.data

    def test_logout(self, app):
        """Test logging out user."""
        email: str = 'logout@test.com'
        password: str = 'password'
        user: User = User(
            email=email,
            password=password,
            confirmed=True
        )  # type: ignore

        with app.app_context():
            user.save()

        client = app.test_client()
        client.post(
            '/auth/login',
            data={
                'email': email,
                'password': password,
                'remember_me': True
            },
            follow_redirects=True
        )

        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        assert b'<a href= /auth/login>Log In</a>' in response.data
