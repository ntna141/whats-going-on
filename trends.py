import os
from dotenv import load_dotenv
from openai import OpenAI
import praw
import json

# Load environment variables
load_dotenv()

# Set up API clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="TrendMonitor/1.0"
)

def get_trending_posts(subreddits, limit=10):
    trending_posts = {}
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        trending_posts[subreddit_name] = [
            {
                'title': post.title,
                'url': post.url,
                'score': post.score,
                'num_comments': post.num_comments
            }
            for post in subreddit.hot(limit=limit)
        ]
    return trending_posts

def analyze_trends(trending_posts):
    # Flatten the list of posts from all subreddits
    all_posts = [post for subreddit in trending_posts.values() for post in subreddit]
    
    # Sort posts by score and number of comments
    sorted_posts = sorted(all_posts, key=lambda x: (x['score'], x['num_comments']), reverse=True)
    
    # Take top 10 posts
    top_posts = sorted_posts[:10]
    
    prompt = f"""Analyze the following trending Reddit posts and select the 3 most interesting ones that would appeal to a broad audience. Consider factors like novelty, cultural impact, and potential for engaging content. Ignore sports and celebs content.

    Posts: {json.dumps(top_posts, indent=2)}

    Output your response as a JSON object with the top 5 posts, including their titles and URLs. Nothing else.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert trend analyst with a keen understanding of what makes content engaging and shareable."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(completion.choices[0].message.content)

def main():
    subreddits = ["news", "worldnews", "technology", "science"]  # Add or modify subreddits as needed
    trending_posts = get_trending_posts(subreddits)
    selected_trends = analyze_trends(trending_posts)
    
    print(json.dumps(selected_trends, indent=2))

    return selected_trends

if __name__ == "__main__":
    main()