import nltk
import os
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize VADER SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(posts):
    results = []
    for post in posts:
        # Get sentiment scores
        sentiment_score = sia.polarity_scores(post['content'])['compound']
        
        # Classify sentiment based on the compound score
        sentiment = "POSITIVE" if sentiment_score >= 0 else "NEGATIVE"
        
        # Append results
        results.append({
            "title": post['title'],
            "content": post['content'],
            "sentiment": sentiment,
            "score": sentiment_score
        })
    return results
