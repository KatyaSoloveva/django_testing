from http import HTTPStatus

from pytils.translit import slugify

from .services import (ADD_URL, DELETE_URL, EDIT_URL,
                       LOGIN_URL, SLUG, SUCCESS_URL, ServicesClass)
from notes.models import Note
from notes.forms import WARNING


class TestLogic(ServicesClass):

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(ADD_URL, data=self.form_data)
        redirect_url = f'{LOGIN_URL}?next={ADD_URL}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(SLUG + WARNING))
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он
        формируется автоматически.
        """
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        self.assertEqual(Note.objects.count(), self.count_notes_before)
        response = self.author_client.post(EDIT_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки,"""
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.count_notes_before - 1)

    def test_reader_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.assertEqual(Note.objects.count(), self.count_notes_before)
        response = self.reader_client.post(EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_from_db = Note.objects.get(slug=SLUG)
        self.assertEqual(self.note.title, self.note_from_db.title)
        self.assertEqual(self.note.text, self.note_from_db.text)
        self.assertEqual(self.note.slug, self.note_from_db.slug)
        self.assertEqual(self.note.author, self.note_from_db.author)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалть чужие заметки."""
        response = self.reader_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.count_notes_before)
