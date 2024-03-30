import warnings
warnings.filterwarnings('ignore')

import praw

from mls_reddit_bot import constants


def get_reddit_client():
    # authenticate and gain client; environment variables expected are:
    #    praw_client_id = ...
    #    praw_client_secret = ...
    #    praw_password = ...
    #    praw_username = ...
    client = praw.Reddit(
        redirect_uri=f"https://www.reddit.com/r/{constants.REDDIT_SUBREDDIT}/",
        user_agent=f"MLS_Match_Thread_Bot by u/{constants.REDDIT_USERNAME}",
    )
    assert client.user.me() == constants.REDDIT_USERNAME, "failed to authenticate"
    return client
