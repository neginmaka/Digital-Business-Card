import pytest

from flask_app import app


def get_endpoints():
    endpoints = {"/",
                 "/register",
                 "/login",
                 "/about",
                 "/contact",
                 "/testuser"}
    return endpoints


def redirect_to_login_endpoints():
    endpoints = {"/testuser/admin"}
    return endpoints


def redirect_to_home_endpoints():
    endpoints = {"/logout"}
    return endpoints


class TestRoutes:
    @pytest.mark.parametrize('endpoint', get_endpoints())
    def test_get_requests(self, endpoint):
        response = app.test_client().get(endpoint)
        assert response.status_code == 200

    @pytest.mark.parametrize('endpoint', redirect_to_login_endpoints())
    def test_redirect_to_login_work_correctly(self, endpoint):
        response = app.test_client().get(endpoint)
        assert "/login?next" in response.location
        assert response.status_code == 302

    @pytest.mark.parametrize('endpoint', redirect_to_home_endpoints())
    def test_redirect_to_home_work_correctly(self, endpoint):
        response = app.test_client().get(endpoint)
        assert response.location == "/"
        assert response.status_code == 302
