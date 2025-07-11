import pytest
from app import app, db, Blogpost
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
load_dotenv()
jws_secret_key = os.environ['JWT_SECRET_KEY']
@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///test.db'
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = jws_secret_key

    with app.app_context():
        db.create_all()
    
    yield app.test_client()

    with app.app_context():
        db.drop_all()

@pytest.fixture
def auth_token(client):
    response = client.post('/login', data={'username':'admin','password':'password'})
    return response.json['access_token']

def test_login(client):
    response = client.post('/login', data ={'username':'admin','password':'password'})
    assert response.status_code==200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json

def test_login_invalid(client):
    response = client.post('/login', data ={'username':'admin','password':'wrongpassword'})
    assert response.status_code == 401
    assert 'msg' in response.json

def test_view_posts(client, auth_token):
    with app.app_context():
        post = Blogpost(title='Test Post', content='This is test content',date_posted = datetime.utcnow(), subtitle='Test subtitle', author = 'Test author')
        db.session.add(post)
        db.session.commit()
        response = client.get('/', headers={'Authorization':f'Bearer {auth_token}'})
        assert response.status_code == 200
        assert len(response.data) > 0

def test_add_post(client, auth_token):
    with app.app_context():
        post_data  = {
            'title':'Test post',
            'subtitle':'Test subtitle',
            'author':'Test author',
            'content': 'Test content'
        }
        response = client.post('/addpost', data = post_data, headers={'Authorization':f'Bearer {auth_token}'} )
        assert response.status_code == 302
        new_post = Blogpost.query.filter_by(title='Test post').first()
        assert new_post is not None
        assert new_post.title == 'Test post'
        assert new_post.subtitle == 'Test subtitle'
        assert new_post.author == 'Test author'
        assert new_post.content == 'Test content'

def test_delete_post(client, auth_token):
    with app.app_context():
        post = Blogpost(title='Test Post', content='This is test content',date_posted = datetime.utcnow(), subtitle='Test subtitle', author = 'Test author')
        db.session.add(post)
        db.session.commit()
        response = client.post('/deletepost', data = {'post_id': post.id}, headers={'Authorization':f'Bearer {auth_token}'})
        assert response.status_code == 302
        with app.app_context():
            deleted_post = Blogpost.query.get(post.id)
            assert deleted_post is None