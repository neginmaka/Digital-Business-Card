import pytest

from main_app import app


def get_application_endpoints():
    endpoints = ["/", "/register", "/login", "/about", "/contact",
                 "/<username>/admin", "/<username>/profile", "/<username>"]
    return endpoints


@pytest.mark.parametrize('endpoint', get_application_endpoints())
def test_get_requests(endpoint):
    response = app.test_client().get(endpoint)
    assert response.status_code == 200
