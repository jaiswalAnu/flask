from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from app.models.notes_model import NoteModel, db
from app.utils.logger import get_logger
from app.schemas.notes_schema import note_schema, notes_schema

logger = get_logger('note_routes')
note_bp = Blueprint('note_bp', __name__)
api = Api(note_bp, doc='/swagger', title='Notes API', description='Management of Notes API')

note_model = api.model('note',{
    'title': fields.String(required=True, description='Note title'),
    'content': fields.String(required=True, description='Note Content')
})

@api.route('/notes')
class NoteList(Resource):
    @api.doc('list_routes')
    def get(self):
        '''Retrieving all the notes'''
        notes = NoteModel.query.all()
        return notes_schema.dump(notes), 200
    
    @api.expect(note_model)
    @api.doc('create_note')
    def post(self):
        '''Create a new note'''
        data = request.get_json()
        new_note = NoteModel(title = data['title'], content= data['content'])
        db.session.add(new_note)
        db.session.commit()
        return note_schema.dump(new_note), 201
    
@api.route('/notes/<int:id>')
class NoteDetail(Resource):
    @api.doc('get_note')
    def get(self, id):
        '''Retrieve note by id'''
        note = NoteModel.query.get_or_404(id)
        return note_schema.dump(note), 200
    
    @api.doc('delete_note')
    def delete(self, id):
        '''Delete a note by id'''
        note = NoteModel.query.get_or_404(id)
        db.session.delete(note)
        db.session.commit()
        return {'message':'Note deleted'}, 204
    
