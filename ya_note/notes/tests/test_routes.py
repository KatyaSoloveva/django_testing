from http import HTTPStatus

from .services import (DELETE_URL, DETAIL_URL, EDIT_URL, HOME_URL, LOGIN_URL,
                       LOGOUT_URL, SIGNUP_URL, ServicesClass)


class TestRoutes(ServicesClass):

    def test_pages_availability_for_author(self):
        """Автору заметки доступны все страницы."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_reader(self):
        """
        Доступность страниц для аутентифицированного пользователя.

        Аутентифицированному пользователю (не автору заметки) доступны
        все страницы, кроме редактирования/удаления заметки и страницы
        отдельной заметки.
        """
        not_access_urls = (
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        )
        for url in self.urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                if url in not_access_urls:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        """
        Доступность страниц для анонимного пользователя.

        Анонимному пользователю доступны только главная страница,
        страницы регистрации, входа в учётную запись и выхода из неё.
        При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки анонимный
        пользователь перенаправляется на страницу логина.
        """
        access_urls = (
            HOME_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL,
        )
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                if url in access_urls:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{LOGIN_URL}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(response, redirect_url)
