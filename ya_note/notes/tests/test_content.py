from .services import ADD_URL, EDIT_URL, LIST_URL, ServicesClass
from notes.forms import NoteForm


class TestContent(ServicesClass):

    def test_notes_list_for_author(self):
        """В список заметок юзера попадают его собственные заметки."""
        response = self.author_client.get(LIST_URL)
        object_list_count = response.context['object_list'].count()
        self.assertEqual(object_list_count, 1)
        note_from_list = response.context['object_list'][0]
        self.assertEqual(note_from_list.title, self.note.title)
        self.assertEqual(note_from_list.text, self.note.text)
        self.assertEqual(note_from_list.slug, self.note.slug)
        self.assertEqual(note_from_list.author, self.note.author)

    def test_notes_list_for_reader(self):
        """В список заметок юзера не попадают чужие заметки."""
        response = self.reader_client.get(LIST_URL)
        object_list_count = response.context['object_list'].count()
        self.assertEqual(object_list_count, 0)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ADD_URL,
            EDIT_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
