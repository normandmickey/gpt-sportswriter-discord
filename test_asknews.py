from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
print(TAVILY_API_KEY)

max_results = 5
client = TavilyClient(api_key=TAVILY_API_KEY)
# For basic search:
response = client.search("Cleveland Cavaliers vs Detroit Pistons", search_depth="basic")
# For advanced search:
#response = tavily.search(query="Should I invest in Apple in 2024?", search_depth="advanced")
# Get the search results as context to pass an LLM:
#context = [{"url": obj["url"], "content": obj["content"]} for obj in response.results]
#context = [{"body": obj["content"]} for obj in response.get("results", [])]
context = [{"href": obj["url"], "body": obj["content"]} for obj in response.get("results", [])]
context = str(context)
print(context[:20000])