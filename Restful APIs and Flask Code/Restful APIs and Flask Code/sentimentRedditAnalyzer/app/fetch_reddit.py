import os
import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_reddit_data(topic, limit=10):
    """
    Fetch the latest 'limit' number of posts from Reddit for a given topic.
    Args:
    - topic: The search query (subreddit or keyword).
    - limit: The number of posts to fetch.

    Returns:
    - A list of Reddit posts (title, content, and URL).
    """
    try:
        # Initialize Reddit client
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )

        # Verify Reddit instance
        reddit.read_only = True

        # Fetch posts from Reddit for the topic
        posts = []
        subreddit = reddit.subreddit('all')
        
        for submission in subreddit.search(topic, sort='new', time_filter='all', limit=limit):
            posts.append({
                "title": submission.title,
                "content": submission.selftext or "No content available",  # Handle empty content
                "url": submission.url
            })
        
        return posts
    
    except Exception as e:
        print(f"Error fetching data from Reddit: {e}")
        return []
