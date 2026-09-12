from groq import Groq
from tavily import TavilyClient

from config_runtime import GROQ_API_KEY, TAVILY_API_KEY, logger

GROQ_COMPOUND_MODEL = 'compound-beta-mini'

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
client_tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


def fetch_groq_compound_context(query, *, n_articles=3):
    """Live news context via Groq Compound (agentic web search).

    Replaces the old AskNews lookup. Returns a compact factual briefing with
    inline source attribution, or '' on failure so callers can fall back.
    """
    if not groq_client:
        logger.warning("Groq Compound unavailable: GROQ_API_KEY not set")
        return ''
    try:
        import datetime
        today = datetime.date.today().isoformat()
        response = groq_client.chat.completions.create(
            model=GROQ_COMPOUND_MODEL,
            messages=[{
                'role': 'user',
                'content': (
                    f"Search the web for the latest news (last 24-48 hours, today is {today}) "
                    f"about this sports query: {query}. "
                    "Then report what you actually found: scores, injuries, lineups, betting-relevant "
                    "notes, and recent form. Attribute key facts inline with the source, e.g. (per ESPN). "
                    "You MUST search before answering - do not answer from memory alone. "
                    "Write it as a compact factual briefing of roughly 3 stories, no predictions."
                ),
            }],
            temperature=0.4,
            max_tokens=1200,
        )
        content = (response.choices[0].message.content or '').strip()
        if not content:
            logger.warning("Groq Compound returned empty context for query '%s'", query)
            return ''
        return content
    except Exception as exc:
        logger.warning("Groq Compound lookup failed for query '%s': %s", query, exc)
        return ''


def fetch_asknews_context(query, *, n_articles=3):
    """Back-compat alias: AskNews was replaced by Groq Compound (2026-09-12)."""
    return fetch_groq_compound_context(query, n_articles=n_articles)


def fetch_tavily_context(query):
    if not client_tavily:
        return ''
    try:
        response = client_tavily.search(query=query, search_depth='advanced')
        return [{"href": obj["url"], "body": obj["content"]} for obj in response.get('results', [])]
    except Exception as exc:
        logger.warning("Tavily fallback failed for query '%s': %s", query, exc)
        return ''
