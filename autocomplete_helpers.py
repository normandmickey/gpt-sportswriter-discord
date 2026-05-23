from datetime import datetime as dtdt

from config_runtime import HTTP_TIMEOUT, ODDS_API_KEY, http

FRIENDLY_LABELS = {
    'americanfootball_nfl': 'NFL',
    'americanfootball_ncaaf': 'NCAAF',
    'baseball_mlb': 'MLB',
    'basketball_nba': 'NBA',
    'basketball_wnba': 'WNBA',
    'icehockey_nhl': 'NHL',
    'mma_mixed_martial_arts': 'MMA',
    'soccer_usa_mls': 'MLS',
    'soccer_epl': 'EPL',
    'soccer_uefa_champs_league': 'Champions League',
    'tennis_atp_french_open': 'French Open ATP',
    'tennis_wta_french_open': 'French Open WTA',
}

SPORT_PRIORITY = {
    'americanfootball_nfl': 1,
    'basketball_nba': 2,
    'baseball_mlb': 3,
    'icehockey_nhl': 4,
    'basketball_wnba': 5,
    'soccer_usa_mls': 6,
    'mma_mixed_martial_arts': 7,
    'americanfootball_ncaaf': 8,
    'soccer_epl': 9,
    'tennis_atp_french_open': 10,
    'tennis_wta_french_open': 11,
}


def rank_text_options(options, query, *, key=str):
    query = str(query or '').strip().lower()
    if not query:
        return options[:25]

    def score(item):
        value = key(item).lower()
        if value.startswith(query):
            return (0, len(value))
        token_matches = [token for token in value.split() if token.startswith(query)]
        if token_matches:
            return (1, len(value))
        if query in value:
            return (2, value.index(query), len(value))
        return (9, len(value))

    ranked = sorted(options, key=score)
    filtered = [
        item for item in ranked
        if query in key(item).lower()
        or key(item).lower().startswith(query)
        or any(token.startswith(query) for token in key(item).lower().split())
    ]
    return filtered[:25]


def build_sport_maps(data_sport_keys, included_sports, excluded_leagues):
    sport_choices = []
    league_titles = []
    label_to_key = {}
    sports = []
    for row in data_sport_keys:
        if row['has_outrights'] is False and row['group'] in included_sports and row['key'] not in excluded_leagues:
            key = row['key']
            title = (row.get('title') or row.get('description') or key).strip()
            label = FRIENDLY_LABELS.get(key, title)
            sports.append({
                'key': key,
                'label': label,
                'title': title,
                'description': row.get('description', title),
                'priority': SPORT_PRIORITY.get(key, 999),
            })
    for row in sorted(sports, key=lambda item: (item['priority'], item['label'].lower())):
        key = row['key']
        label = row['label']
        collision_counter = 2
        base_label = label
        while label in label_to_key and label_to_key[label] != key:
            label = f"{base_label} ({collision_counter})"
            collision_counter += 1
        label_to_key[label] = key
        sport_choices.append(label)
        league_titles.append(row['description'])
    sport_choices = [item for n, item in enumerate(sport_choices) if item not in sport_choices[:n]]
    league_titles = [item for n, item in enumerate(league_titles) if item not in league_titles[:n]]
    return sport_choices, league_titles, label_to_key


async def autocomplete_sport_label(ctx, sport_labels):
    return rank_text_options(list(sport_labels), ctx.value or '')


async def autocomplete_league(ctx, leagues):
    return rank_text_options(list(leagues), ctx.value or '')


def _fetch_games_for_sport(sport):
    response = http.get(
        f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals&bookmakers=draftkings&oddsFormat=decimal",
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _fetch_scores_for_sport(sport):
    response = http.get(
        f"https://api.the-odds-api.com/v4/sports/{sport}/scores/?daysFrom=1&apiKey={ODDS_API_KEY}",
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _format_event_label(game, es_time):
    return f"{game['away_team']} @ {game['home_team']} — {es_time.strftime('%a %b %-d %I:%M %p ET')}"[:100]


def _candidate_event_labels(game, es_time):
    label = _format_event_label(game, es_time)
    away = game['away_team']
    home = game['home_team']
    date_text = es_time.strftime('%a %b %-d %I:%M %p ET')
    return [
        label,
        f"{away} vs {home} — {date_text}",
        f"{home} vs {away} — {date_text}",
    ]


def resolve_selected_event(sport_key, selected_label, utc, ept, *, completed=False):
    data_games = _fetch_scores_for_sport(sport_key) if completed else _fetch_games_for_sport(sport_key)
    selected_label = str(selected_label).strip()
    for game in data_games:
        if completed and game.get('completed') is not True:
            continue
        t = game['commence_time']
        utc_time = dtdt(int(t[0:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]), tzinfo=utc)
        es_time = utc_time.astimezone(ept)
        for candidate in _candidate_event_labels(game, es_time):
            if selected_label == candidate:
                return game['id'], candidate
    raise ValueError(f"Could not resolve event for selected label: {selected_label}")


async def get_sport(ctx, utc, ept, label_to_key):
    sport_label = ctx.options['sport']
    sport_key = label_to_key.get(sport_label, sport_label)
    query = ctx.value or ''
    data_games = _fetch_games_for_sport(sport_key)
    games = []
    today = dtdt.now(tz=ept).date()
    for game in data_games:
        t = game['commence_time']
        utc_time = dtdt(int(t[0:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]), tzinfo=utc)
        es_time = utc_time.astimezone(ept)
        if es_time.date() < today or (es_time.date() - today).days > 3:
            continue
        games.append(_format_event_label(game, es_time))
    return rank_text_options(games, query)


async def get_score(ctx, utc, ept, label_to_key):
    sport_label = ctx.options['sport']
    sport_key = label_to_key.get(sport_label, sport_label)
    query = ctx.value or ''
    data_games = _fetch_scores_for_sport(sport_key)
    games = []
    for game in data_games:
        if game['completed'] is True:
            t = game['commence_time']
            utc_time = dtdt(int(t[0:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]), tzinfo=utc)
            es_time = utc_time.astimezone(ept)
            games.append(_format_event_label(game, es_time))
    return rank_text_options(games, query)
