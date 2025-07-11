from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import os

#Generation of random JWT secret key
jwt_secret_key = secrets.token_hex(32)
load_dotenv()
if "JWT_SECRET_KEY" in os.environ:
    os.environ['JWT_SECRET_KEY'] = jwt_secret_key
else:
    with open(".env","a") as env_file:
        env_file.write(f"JWT_SECRET_KEY={jwt_secret_key}\n")
load_dotenv()
# initialise
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

class Blogpost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == "admin" and password== "password":
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({'msg':'Invalid credentials'}), 401
    
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@app.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    return jsonify(msg="Logged out successfully"), 200

@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_id>', methods=['GET'])
@jwt_required()
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)

@app.route('/add')
@jwt_required()
def add():
    return render_template('add.html')

@app.route('/delete')
@jwt_required()
def delete():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('delete.html', posts=posts)

@app.route('/addpost', methods=['POST'])
@jwt_required()
def addpost():
    try:
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']

        post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deletepost', methods=['DELETE','POST'])
@jwt_required()
def deletepost():
    try:
        post_id = request.form.get("post_id")

        post = Blogpost.query.filter_by(id=post_id).first()

        db.session.delete(post)
        db.session.commit()
        
        return redirect(url_for('index'))
    except Exception as e:
            return jsonify({"error": str(e)}), 500

with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)