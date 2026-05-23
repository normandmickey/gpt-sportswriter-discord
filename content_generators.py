from datetime import datetime, timedelta

from autocomplete_helpers import resolve_selected_event
from config_runtime import ODDSMITH_BASE_URL, ODDSMITH_BOT_API_KEY, ODDS_API_KEY, logger
from http_helpers import fetch_odds_json
from llm_helpers import safe_chat_content
from news_helpers import fetch_asknews_context, fetch_tavily_context
from oddsmith_api import fetch_oddsmith_bot_pick, fetch_oddsmith_bot_recap, generate_oddsmith_bot_pick


def ensure_best_bet_line(text):
    cleaned = (text or '').strip()
    if 'Best Bet:' in cleaned:
        return cleaned
    if cleaned:
        return cleaned + '\n\nBest Bet: Pass'
    return 'Best Bet: Pass'


def createMessage(sport_key, text, utc, ept):
    gameId, match = resolve_selected_event(sport_key, text, utc, ept)
    official_pick = fetch_oddsmith_bot_pick(ODDSMITH_BASE_URL, ODDSMITH_BOT_API_KEY, sport_key, gameId)
    if not official_pick:
        official_pick = generate_oddsmith_bot_pick(ODDSMITH_BASE_URL, ODDSMITH_BOT_API_KEY, sport_key, gameId)
    if official_pick:
        line_bits = [f"Odd$mith Best Bet: {official_pick.get('market', '').strip()}".strip()]
        if official_pick.get('line'):
            line_bits[-1] = f"{line_bits[-1]} {official_pick.get('line', '').strip()}".strip()
        parts = [match, '', line_bits[0]]
        if official_pick.get('confidence'):
            parts.append(f"Confidence: {official_pick['confidence']}")
        reason = (official_pick.get('reason') or '').strip()
        analysis = (official_pick.get('analysis') or '').strip()
        if reason:
            parts.extend(['', reason])
        if analysis:
            parts.extend(['', analysis])
        if official_pick.get('game_url'):
            parts.extend(['', f"More: {official_pick['game_url']}"])
        parts.extend(['', '— GPT SportsWriter by Odd$mith | https://oddsmith.net'])
        image_url = (official_pick.get('image_url') or '').strip()
        if image_url and image_url.startswith('/media/'):
            image_url = ODDSMITH_BASE_URL.rstrip('/') + image_url
        if image_url:
            parts.extend(['', f"Image: {image_url}"])
        return '\n'.join(parts).strip()
    messages = []
    messages.append({
        "role": "system",
        "content": (
            "You are GPT SportsWriter, a sharp sports betting writer for Discord. "
            "Sound confident, conversational, and readable. Favor the older cleaner style: a strong opening, "
            "a short handicap, and a clear best bet. No markdown tables. No fake stats. No bloated formatting. "
            "Use short paragraphs and compact bullets only when they help. Keep it under 1200 characters."
        ),
    })
    messages.append({"role": "user", "content": match})
    odds = str(fetch_odds_json(
        f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&eventIds={gameId}&regions=us&markets=totals,h2h,spreads&bookmakers=draftkings,fanduel,betrivers&oddsFormat=decimal"
    ))

    context = fetch_asknews_context(match, n_articles=3)
    if not context:
        context = fetch_tavily_context(text)
    messages.append({
        "role": "user",
        "content": (
            "Write a concise Discord-ready betting preview for this matchup. Use a natural headline if helpful, then 1-2 short paragraphs and optional short bullets. "
            "Your final line MUST begin with 'Best Bet:' exactly. This is mandatory every time. "
            "If the evidence is weak, write 'Best Bet: Pass' and say why briefly. "
            "Do not hedge without giving a clear Best Bet or Pass. Do not use tables. "
            "If this is preseason or otherwise noisy, acknowledge the uncertainty like a real bettor would. "
            "Only use facts supported by the provided context and odds snapshot.\n\n"
            f"Context: {context}\n\nOdds: {odds}\n\nMatchup: {match}"
        ),
    })
    reply = ensure_best_bet_line(safe_chat_content(messages))
    logger.info("Generated prediction for %s", match)
    return reply


def createProp(sport_key, text, utc, ept):
    _game_id, match = resolve_selected_event(sport_key, text, utc, ept)
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    context = fetch_asknews_context("best prop bets for the text " + match, n_articles=3)
    messages.append({"role": "user", "content": "Write a short article outlining the best individual player prop bets for the following matchup. List the odds and probability. Give your best bet based on the context provided only mention play prop bets that are referenced in the context and mention the sportsbook. The response should be in markdown format." + context + " " + match})
    return safe_chat_content(messages)


def createParlay(sport_key, text):
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    context = fetch_asknews_context("same game parlay " + text, n_articles=3)
    messages.append({"role": "user", "content": "Write a short article outlining the best same game parlay for the following matchup. List the odds and probability. Give your best bet based on the context provided only mention parlays referenced in the context and include the sportsbook. Your response should be in markdown format." + context + " " + text})
    return safe_chat_content(messages)


def topNews(sport_key):
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": sport_key})
    context = fetch_asknews_context(sport_key, n_articles=3)
    messages.append({"role": "user", "content": "Write a funny, but accurate article briefly summarizing the various articles. Each article is enclosed in the <doc> </doc> tag. Ignore redundant articles. Your response should be in markdown format." + context + " " + sport_key})
    return safe_chat_content(messages)


def createRecap(sport_key, text, utc=None, ept=None):
    resolved_match = text
    game_id = ''
    if utc is not None and ept is not None:
        try:
            game_id, resolved_match = resolve_selected_event(sport_key, text, utc, ept, completed=True)
            logger.info("Recap resolved event for %s: %s -> %s", sport_key, resolved_match, game_id)
        except Exception as exc:
            logger.warning("Recap event resolution failed for %s / %s: %s", sport_key, text, exc)
    if game_id:
        recap_payload = fetch_oddsmith_bot_recap(ODDSMITH_BASE_URL, ODDSMITH_BOT_API_KEY, sport_key, game_id)
        if recap_payload and recap_payload.get('recap'):
            logger.info(
                "Using Odd$mith recap for %s/%s (stored=%s provider=%s)",
                sport_key,
                game_id,
                recap_payload.get('stored'),
                recap_payload.get('provider', ''),
            )
            return recap_payload['recap']
        logger.warning("Odd$mith recap lookup missed for %s/%s; falling back locally", sport_key, game_id)

    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": resolved_match})
    context = fetch_asknews_context("final score of the following game " + resolved_match, n_articles=3)
    messages.append({"role": "user", "content": "Write a short, humorous article recapping the results following matchup include the score and highlights. Pay specific attention to the articles and only include information from context provided that is related to the game in question do not make up any details. Your response should be in markdown format. " + context + " " + resolved_match})
    logger.warning("Using local recap fallback for %s / %s", sport_key, resolved_match)
    return safe_chat_content(messages)


def answerTrivia(text):
    messages = []
    messages.append({"role": "system", "content": "You are an AI sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    context = fetch_tavily_context(text)
    context = str(context)
    messages.append({"role": "user", "content": "Given the following context answer the sports trivia question at the end. Be humorous but accurate. If the question is not sports related, politely refuse to answer. Your response should be in markdown format." + context + " " + text})
    return safe_chat_content(messages)
