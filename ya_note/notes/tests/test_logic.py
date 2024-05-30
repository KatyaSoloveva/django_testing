from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Просто юзер')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        cls.count_notes_before = Note.objects.count()
        cls.add_note = reverse('notes:add')
        cls.edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_note = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        response = self.author_client.post(self.add_note, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), self.count_notes_before + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_note, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.add_note}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_note, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), self.count_notes_before)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_note, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_note, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_note)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), self.count_notes_before - 1)

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(self.edit_note, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_from_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.title, self.note_from_db.title)
        self.assertEqual(self.note.text, self.note_from_db.text)
        self.assertEqual(self.note.slug, self.note_from_db.slug)

    def test_reader_cant_delete_note(self):
        response = self.reader_client.post(self.delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.count_notes_before)
