from app.extensions import ma
from app.models.notes_model import NoteModel

class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NoteModel
        load_instance = True

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)