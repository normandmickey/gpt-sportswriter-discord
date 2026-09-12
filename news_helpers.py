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
                    f"Today's date is {today}. Use live web search to gather recent news "
                    f"(last 24-48 hours) for this sports query: {query}. "
                    "Return only a compact factual briefing of what you found: scores, injuries, "
                    "lineups, betting-relevant notes, and recent form. Attribute key facts inline "
                    f"with the source, e.g. (per ESPN). Cover roughly {n_articles} stories. "
                    "Do not write an article or make predictions. If you find nothing relevant, "
                    "say 'No recent news found'."
                ),
            }],
            temperature=0.3,
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
