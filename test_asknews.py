import os
from datetime import datetime as dtdt
from dotenv import load_dotenv
from asknews_sdk import AskNewsSDK
from datetime import datetime, timedelta

load_dotenv()
ASKNEWS_CLIENT_ID = os.environ.get('ASKNEWS_CLIENT_ID')
ASKNEWS_CLIENT_SECRET = os.environ.get('ASKNEWS_CLIENT_SECRET')
query = "Buffalo Bills"
start = (datetime.now() - timedelta(hours=48)).timestamp()
end = datetime.now().timestamp()

ask = AskNewsSDK(
        client_id=ASKNEWS_CLIENT_ID,
        client_secret=ASKNEWS_CLIENT_SECRET,
        scopes=["news"]
)


#context = ask.news.search_news(query=query, method='kw', return_type='string', n_articles=10, categories=["Sports"], start_timestamp=int(start), end_timestamp=int(end)).as_string
newsArticles = ask.news.search_news(query, method='kw', return_type='dicts', n_articles=3, categories=["Sports"], start_timestamp=int(start), end_timestamp=int(end)).as_dicts
for article in newsArticles:
    print(article.summary)
        