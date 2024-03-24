import warnings
warnings.filterwarnings('ignore')

import praw

REDDIT_USERNAME = "MLS_Reddit_Bot"
REDDIT_SUBREDDIT = "MLS_Reddit_Bot"

def get_reddit_client():
    # authenticate and gain client; environment variables expected are:
    #    praw_client_id = ...
    #    praw_client_secret = ...
    #    praw_password = ...
    #    praw_username = ...
    client = praw.Reddit(
        redirect_uri=f"https://www.reddit.com/r/{REDDIT_SUBREDDIT}/",
        user_agent=f"MLS_Match_Thread_Bot by u/{REDDIT_USERNAME}",
    )
    assert client.user.me() == REDDIT_USERNAME, "failed to authenticate"
    return client
