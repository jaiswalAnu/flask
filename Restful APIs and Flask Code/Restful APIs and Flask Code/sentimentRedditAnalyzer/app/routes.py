from flask import Blueprint, request, jsonify, render_template
from app.fetch_reddit import fetch_reddit_data
from app.analysis import analyze_sentiment
from app.graphs import generate_graphs
from app import db, cache
from app.models import SentimentAnalysis
from app.logger import configure_logger
sentiment_bp = Blueprint(
    'sentiment', 
    __name__,
    template_folder='templates'
)

logger = configure_logger()  # Get the logger instance

@sentiment_bp.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@sentiment_bp.route('/analyze', methods=['POST', 'GET'])
@cache.cached(timeout=3600, key_prefix=lambda: request.form.get('topic') or request.args.get('topic', ''))
def analyze_sentiment_route():
    # Ensure topic and limit are handled for both GET and POST requests
    topic = request.form.get('topic') or request.args.get('topic')
    limit = int(request.form.get('num_records', 10))  # Default limit if not provided

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # Check if data exists in Postgres
    sentiment_results = SentimentAnalysis.query.filter_by(topic=topic).order_by(SentimentAnalysis.created_at.desc()).limit(limit).all()

    if sentiment_results:
        logger.info("Data fetched from sentimental analysis table")
        sentiment_results = [
            {
                "title": record.title,
                "content": record.content,
                "sentiment": record.sentiment,
                "score": record.score
            }
            for record in sentiment_results
        ]
    else:
        # Fetch Reddit data
        posts = fetch_reddit_data(topic, limit)

        # Analyze sentiment
        sentiment_results = analyze_sentiment(posts)

        # Save results to Postgres
        for result in sentiment_results:
            db.session.add(SentimentAnalysis(
                topic=topic,
                title=result['title'],
                content=result['content'],
                sentiment=result['sentiment'],
                score=result['score']
            ))
        db.session.commit()

    # Generate graphs (bar chart and word cloud)
    bar_chart_b64, word_cloud_b64 = generate_graphs(sentiment_results, topic)

    # Render the template with the data
    return render_template(
        'index.html',
        topic=topic,
        sentiment_results=sentiment_results,
        bar_chart_b64=bar_chart_b64,
        word_cloud_b64=word_cloud_b64
    )
  
