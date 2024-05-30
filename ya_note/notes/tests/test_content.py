from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Просто юзер')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        usres_statuses = (
            (self.author, 1),
            (self.reader, 0),
        )
        for user, quantity in usres_statuses:
            self.user_client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.user_client.get(url)
                object_list_count = response.context['object_list'].count()
                self.assertEqual(object_list_count, quantity)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
