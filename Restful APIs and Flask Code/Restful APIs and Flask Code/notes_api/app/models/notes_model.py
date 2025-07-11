from app.extensions import db
class NoteModel(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.String(255), nullable = False)

    def __repr__(self):
        return f'<Note: {self.title}>'