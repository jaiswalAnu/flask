import unittest
from app import create_app
from app.extensions import db
from app.models.notes_model import NoteModel

class NotesApiTestCase(unittest.TestCase):
    def setUp(self):
        '''set up the test environment, create flask app, setting up
        the test client for simulating api calls, push the app context from db 
        interactions and initialize the db'''
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        '''clean up after each test case, removal of db session, dropping of all the tables'''
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_note(self):
        '''Test the creation of a new note'''
        response = self.client.post("/api/notes", json={'title': 'Test Note', 'content': 'Test Content'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Test Note',response.get_data(as_text=True))

    def test_get_notes(self):
        note = NoteModel(title='Test Note', content='Test Content')
        db.session.add(note)
        db.session.commit()
        response = self.client.get('/api/notes')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Note', response.get_data(as_text=True))


if __name__ =='__main__':
    unittest.main()
