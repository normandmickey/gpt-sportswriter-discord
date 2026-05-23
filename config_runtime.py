import logging
import os

import requests
import requests_cache
from dotenv import load_dotenv

requests_cache.install_cache('api_cache', expire_after=900)
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('gptsportswriter-discord')

ODDS_API_KEY = os.environ.get('ODDS_API_KEY')
ASKNEWS_CLIENT_ID = os.environ.get('ASKNEWS_CLIENT_ID')
ASKNEWS_CLIENT_SECRET = os.environ.get('ASKNEWS_CLIENT_SECRET')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
ODDSMITH_BASE_URL = os.environ.get('ODDSMITH_BASE_URL', 'https://oddsmith.net')
ODDSMITH_BOT_API_KEY = os.environ.get('ODDSMITH_BOT_API_KEY')
TOPGG_TOKEN = os.environ.get('TOPGG_TOKEN')

required_env = {
    'ODDS_API_KEY': ODDS_API_KEY,
    'ASKNEWS_CLIENT_ID': ASKNEWS_CLIENT_ID,
    'ASKNEWS_CLIENT_SECRET': ASKNEWS_CLIENT_SECRET,
    'OPENAI_API_KEY': OPENAI_API_KEY,
    'DISCORD_BOT_TOKEN': DISCORD_BOT_TOKEN,
    'GROQ_API_KEY': GROQ_API_KEY,
}
missing_env = [key for key, value in required_env.items() if not value]
if missing_env:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_env)}")

http = requests.Session()
HTTP_TIMEOUT = 25
