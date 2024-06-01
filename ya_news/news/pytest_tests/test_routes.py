from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
CLIENT = pytest.lazy_fixture('client')
HOME_URL = pytest.lazy_fixture('home_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')


@pytest.mark.parametrize(
    'url, parametrized_client, status',
    (
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
    )
)
def test_pages_availability(url, parametrized_client, status):
    """
    Доступность страниц для различных пользователей.

    Страницы удаления и редактирования комментария доступны только автору
    комментария. Главная страница, страница отдельной новости, страницы
    регистрации, входа в учётную запись и выхода из неё доступны анонимному
    пользователю.
    """
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url',
    (
        EDIT_URL,
        DELETE_URL,
    )
)
def test_redirects(login_url, url, client):
    """
    Проверка редиректа.

    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
