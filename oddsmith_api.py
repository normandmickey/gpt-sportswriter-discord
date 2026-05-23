from config_runtime import HTTP_TIMEOUT, logger, http


def fetch_oddsmith_bot_recap(base_url, api_key, sport_key, event_id):
    if not base_url or not api_key:
        return None
    url = f"{base_url.rstrip('/')}/api/bot-recap/"
    try:
        response = http.get(
            url,
            params={"sport": sport_key, "event_id": event_id},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=HTTP_TIMEOUT,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        if not data.get('found'):
            return None
        return data
    except Exception as exc:
        logger.warning("Odd$mith bot recap lookup failed for %s/%s: %s", sport_key, event_id, exc)
        return None


def fetch_oddsmith_bot_pick(base_url, api_key, sport_key, event_id):
    if not base_url or not api_key:
        return None
    url = f"{base_url.rstrip('/')}/api/bot-pick/"
    try:
        response = http.get(
            url,
            params={"sport": sport_key, "event_id": event_id},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=HTTP_TIMEOUT,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        if not data.get('found'):
            return None
        return data
    except Exception as exc:
        logger.warning("Odd$mith bot API lookup failed for %s/%s: %s", sport_key, event_id, exc)
        return None



def generate_oddsmith_bot_pick(base_url, api_key, sport_key, event_id):
    if not base_url or not api_key:
        return None
    if (sport_key or '').startswith('tennis_'):
        logger.info("Odd$mith bot generate disabled for tennis event %s/%s", sport_key, event_id)
        return None
    url = f"{base_url.rstrip('/')}/api/bot-pick/generate/"
    try:
        response = http.post(
            url,
            json={"sport": sport_key, "event_id": event_id},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=HTTP_TIMEOUT,
        )
        if response.status_code in {400, 404}:
            logger.info("Odd$mith bot generate skipped for %s/%s: %s", sport_key, event_id, response.status_code)
            return None
        response.raise_for_status()
        data = response.json()
        if not data.get('found'):
            return None
        return data
    except Exception as exc:
        logger.warning("Odd$mith bot API generate failed for %s/%s: %s", sport_key, event_id, exc)
        return None
