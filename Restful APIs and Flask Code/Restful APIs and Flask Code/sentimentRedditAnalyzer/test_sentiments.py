import pytest
from flask import Flask
from app import create_app, db
from app.models import SentimentAnalysis
from app.analysis import analyze_sentiment
from app.fetch_reddit import fetch_reddit_data
from unittest.mock import patch


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_sentiments.db'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_analyze_sentiment():
    posts = [
        {
            "content": "I am looking for subcontracting job in computer programming and data sciences. I have many years of quantitative analysis experience in private sector working with large dataset using C++ / Python and machine learning, plus project management. This is my first time looking into this area. Any suggestion will be much appreciated. I am US citizen.",
            "title": "Looking for subcontracting job in computer programming and data sciences"
        },
        {
            "title": "[Hiring] [Remote] [India] - Software Engineer I\n",
            "content": "* Experience : 1+ years\n* Skills : GoLang, Python, Java, NodeJS, TypeScript, REST APIs\n\n**Check more details and apply -**\n\n[https://peerlist.io/company/c2fo/careers/software-engineer-i/jobhmql89q79dolk63d8q8jgamjmpr](https://peerlist.io/company/c2fo/careers/software-engineer-i/jobhmql89q79dolk63d8q8jgamjmpr)\n\n",
        }
    ]
    results = analyze_sentiment(posts)
    assert len(results) == 2
    assert results[0]['sentiment'] == 'POSITIVE'
    assert results[1]['sentiment'] == 'POSITIVE'


def test_analyze_route(client):
    with patch('app.fetch_reddit.fetch_reddit_data') as mock_fetch:
        mock_fetch.return_value = [
          {
               "title":"I go to Loyola Maryland and don't know what to major",
            "content":"I enjoy Finance and tech. I was aiming to make the most money out of college and was stuck between data science or Finance. Any help?",
          }

        ]
        response = client.post('/api/sentiment/analyze', data={'topic': 'science', 'num_records': 1})
        assert response.status_code == 200

def test_database_integration(client):
    with client.application.app_context():
        new_record = SentimentAnalysis(
            topic='science',
            title = "I go to Loyola Maryland and don't know what to major",
            content = "I enjoy Finance and tech. I was aiming to make the most money out of college and was stuck between data science or Finance. Any help?",
            sentiment='POSITIVE',
            score=0.5994
        )
        db.session.add(new_record)
        db.session.commit()

        record = SentimentAnalysis.query.filter_by(topic='science').first()
        assert record is not None
        assert record.sentiment == 'POSITIVE'




def test_invalid_input(client):
    response = client.post('/api/sentiment/analyze', data={})
    assert response.status_code == 400
    assert 'Topic is required' in response.data.decode('utf-8')
