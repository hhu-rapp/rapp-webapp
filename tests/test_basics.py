from flask import current_app


class TestBasics():
    def test_app_exists(self):
        assert current_app is not None

    def test_app_is_testing(self, app):
        assert app.config['TESTING']
