from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url,
                                            form_data):
    count_comments_before = Comment.objects.count()
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == count_comments_before


def test_auth_user_can_create_comment(author_client, detail_url,
                                      form_data):
    count_comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == count_comments_before + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == form_data['news']
    assert comment.author == form_data['author']


def test_user_cant_use_bad_words(not_author_client, detail_url):
    count_comments_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(detail_url, data=bad_words_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    assert Comment.objects.count() == count_comments_before


def test_author_can_edit_comment(author_client, detail_url, form_data,
                                 comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == form_data['news']
    assert comment.author == form_data['author']


def test_author_can_delete_comment(author_client, detail_url,
                                   comment):
    count_comments_before = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == count_comments_before - 1


def test_not_author_cant_edit_comment(not_author_client, form_data,
                                      comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_not_author_cant_delete_comment(not_author_client, comment):
    count_comments_before = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments_before
