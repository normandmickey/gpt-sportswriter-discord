from config_runtime import HTTP_TIMEOUT, http


def fetch_odds_json(url):
    response = http.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    return response.json()
