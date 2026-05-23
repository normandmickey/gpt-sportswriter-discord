from asknews_sdk import AskNewsSDK
from tavily import TavilyClient

from config_runtime import ASKNEWS_CLIENT_ID, ASKNEWS_CLIENT_SECRET, TAVILY_API_KEY, logger

ask = AskNewsSDK(
    client_id=ASKNEWS_CLIENT_ID,
    client_secret=ASKNEWS_CLIENT_SECRET,
    scopes=["news"],
)
client_tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


def fetch_asknews_context(query, *, n_articles=3):
    try:
        articles = ask.news.search_news(
            query,
            method='kw',
            return_type='dicts',
            n_articles=n_articles,
            categories=['Sports'],
        ).as_dicts
        return ''.join(getattr(article, 'summary', '') for article in articles)
    except Exception as exc:
        logger.warning("AskNews lookup failed for query '%s': %s", query, exc)
        return ''


def fetch_tavily_context(query):
    if not client_tavily:
        return ''
    try:
        response = client_tavily.search(query=query, search_depth='advanced')
        return [{"href": obj["url"], "body": obj["content"]} for obj in response.get('results', [])]
    except Exception as exc:
        logger.warning("Tavily fallback failed for query '%s': %s", query, exc)
        return ''
