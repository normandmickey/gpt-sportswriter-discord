import time

from config_runtime import TOPGG_TOKEN, http, logger

TOPGG_API_BASE = 'https://top.gg/api'
TOPGG_MIN_POST_INTERVAL_SECONDS = 300
_last_topgg_post_at = 0.0


def post_topgg_stats(bot, *, force: bool = False) -> bool:
    global _last_topgg_post_at
    if not TOPGG_TOKEN:
        return False
    now = time.time()
    if not force and now - _last_topgg_post_at < TOPGG_MIN_POST_INTERVAL_SECONDS:
        return False
    if not bot.user:
        return False
    guild_count = len(bot.guilds)
    shard_count = bot.shard_count or 1
    payload = {
        'server_count': guild_count,
        'shard_count': shard_count,
    }
    headers = {
        'Authorization': TOPGG_TOKEN,
        'Content-Type': 'application/json',
    }
    url = f"{TOPGG_API_BASE}/bots/{bot.user.id}/stats"
    try:
        response = http.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        _last_topgg_post_at = now
        logger.info('Posted Top.gg stats: guilds=%s shards=%s', guild_count, shard_count)
        return True
    except Exception as exc:
        logger.warning('Top.gg stats post failed: %s', exc)
        return False
