import discord
import os, requests, json, pytz
from datetime import datetime as dtdt
import functools, asyncio, random
import requests_cache
import time
from dotenv import load_dotenv
import requests_cache
from groq import Groq
from asknews_sdk import AskNewsSDK
from datetime import datetime, timedelta
from tavily import TavilyClient
from openai import OpenAI
from pagination import Pagination

requests_cache.install_cache('api_cache', expire_after=900)

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

ept = pytz.timezone('US/Eastern')
utc = pytz.utc
# str format
#fmt = '%Y-%m-%d %H:%M:%S %Z%z'
fmt = '%Y-%m-%d'
GROQ_GPT_MODEL = "llama-3.3-70b-versatile"
OPENAI_GPT_MODEL = "gpt-4o"
ODDS_API_KEY = os.environ.get('ODDS_API_KEY')
ASKNEWS_CLIENT_ID = os.environ.get('ASKNEWS_CLIENT_ID')
ASKNEWS_CLIENT_SECRET = os.environ.get('ASKNEWS_CLIENT_SECRET')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

clientTavily = TavilyClient(api_key=TAVILY_API_KEY)


ask = AskNewsSDK(
        client_id=ASKNEWS_CLIENT_ID,
        client_secret=ASKNEWS_CLIENT_SECRET,
        scopes=["news"]
)

referral_links = ["BetUS - 125% Sign Up Bonus! - https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/","https://cash.app The CashApp is the best way to send money for free. Enter the code WPVJMVS when you sign up and we'll send you $5 when you try it.","https://www.draftkings.com/r/normandmickey","Get $50 on FanDuel Sportsbook in Bonus Bets! Terms apply. Make sure to use my invite link! https://fndl.co/jcafr4b","https://www.ny.betmgm.com/en/mobileportal/invitefriendssignup?invID=5387173","https://caesars.com/sportsbook-and-casino/referral?AR=RAF-BEG-AAV","https://fanatics.onelink.me/5kut/xxyt95qs"]
#referral_links = ["BetUS - 125% Sign Up Bonus! - https://tinyurl.com/GPTSW2","https://cash.app The CashApp is the best way to send money for free. Enter the code WPVJMVS when you sign up and we'll send you $5 when you try it."]
#referral_links = ["BetUS - 125% Sign Up Bonus! - https://record.revmasters.com/_8ejz3pKmFDtD3TEmsPWI0WNd7ZgqdRLk/1/"]

dataSportKeys = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}")
dataSportKeys = dataSportKeys.json()

sport_keys = []
leagues = []

includedSports = ['American Football',
                  'Aussie Rules',
                  'Basketball',
                  'Boxing',
                  'Ice Hockey',
                  'Mixed Martial Arts',
                  'Rugby League',
                  'Soccer',
                  'Tennis']

excludedLeagues = ['icehockey_sweden_hockey_league',
                   'soccer_brazil_serie_b',
                   'soccer_korea_kleague1',
                   'soccer_mexico_ligamx',
                   'soccer_norway_eliteserien',
                   'soccer_spain_segunda_division',
                   'soccer_sweden_superettan',
                   'soccer_argentina_primera_division',
                   'soccer_brazil_campeonato',
                   'soccer_chile_campeonato',
                   'soccer_china_superleague',
                   'soccer_conmebol_copa_america',
                   'soccer_conmebol_copa_libertadores',
                   'soccer_finland_veikkausliiga',
                   'soccer_japan_j_league',
                   'soccer_league_of_ireland',
                   'soccer_sweden_allsvenskan',
                   'soccer_uefa_european_championship',
                   'soccer_belgium_first_div',
                   'soccer_denmark_superliga',
                   'soccer_efl_champ',
                   'soccer_england_efl_cup',
                   'soccer_englane_league1',
                   'soccer_england_league2',
                   'soccer_france_ligue_one',
                   'soccer_netherlands_eredivisie',
                   'soccer_turkey_super_league',
                   'soccer_uefa_champs_league_qualification',
                   'soccer_ufea_europa_conference_league',
                   'soccer_spl',
                   'baseball_milb',
                   'baseball_npb',
                   'soccer_austria_bundesliga',
                   'soccer_england_league1',
                   'soccer_germany_bundesliga',
                   'soccer_germany_bundesliga2',
                   'soccer_germany_liga3',
                   'soccer_greece_super_league',
                   'soccer_italy_serie_a',
                   'soccer_poland_ekstraklasa',
                   'soccer_portugal_primeira_liga',
                   'soccer_switzerland_superleague'
   
]
for i in range(len(dataSportKeys)):
    if (dataSportKeys[i]['has_outrights'] is False and dataSportKeys[i]['group'] in includedSports and dataSportKeys[i]['key'] not in excludedLeagues):
       sport_keys.append(dataSportKeys[i]['key'])
       leagues.append(dataSportKeys[i]['description'])

sport_keys = [i for n, i in enumerate(sport_keys) if i not in sport_keys[:n]]
leagues = [i for n, i in enumerate(leagues) if i not in leagues[:n]]


groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

openai_client = OpenAI(
   api_key=os.environ.get("OPENAI_API_KEY")
)


def chat_completion_request(messages):
    print(messages)
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_GPT_MODEL,
            messages=messages,
            max_tokens=500
        )
        print("Groq: " + str(response))
        return response
    except:
        #print("Unable to generate ChatCompletion response")
        #print(f"Exception: {e}")
        response = openai_client.chat.completions.create(
           model=OPENAI_GPT_MODEL,
           messages=messages,
           max_tokens=500,
           temperature=0.3
        )
        print("OpenAI: " + str(response))
        return response
   
def createMessage(sport_key, text):
    #print("game: " + text)
    odds = ""
    context = ""
    start = (datetime.now() - timedelta(hours=24)).timestamp()
    end = datetime.now().timestamp()
    game = text.split(':')
    gameId = game[0]
    #print("game id: " + gameId)
    match = game[1]
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate and use a lot of sports betting lingo. Limit your response to 1500 characters or less."})
    messages.append({"role": "user", "content": match})
    dataGames = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&eventIds={gameId}&regions=us&markets=totals,h2h,spreads&bookmakers=draftkings,fanduel,betrivers&oddsFormat=decimal")
    odds = str(dataGames.json())
    try:
      newsArticles = ask.news.search_news(match, method='kw', return_type='dicts', n_articles=3, categories=["Sports"], premium=True, start_timestamp=int(start), end_timestamp=int(end)).as_dicts
      for article in newsArticles:
        context += article.summary
        #print(article.summary)
      #print("Odds: " + odds)
      #print("AskNews: " + context)
    except:
      try:
        response = clientTavily.search(query=text, search_depth="advanced")
        context = [{"href": obj["url"], "body": obj["content"]} for obj in response.get("results", [])]
        #print("Tavily: " + context)
      except:
        context = ""
      #print("Odds: " + odds)
      #print("Tavily: " + context)
    messages.append({"role": "user", "content": "Write a brief, humorous article outlining the odds and statistics for the following matchup.  Give your best bet based on the context provided take into account that underdogs win about 41 percent of the time in baseball and hockey, 35 percent in football and 25 percent in baskeball.  Your article should contain as much detail and statistics as possible yet humorous and sarcastic. Do not make anything up, if the context doesn't contain information relevant to the question politely and  humorously refuse to give a prediction. If the context is not relevant to the question politely refuse to answer the question. Your response should be in markdown format. Be funny and sarcastic." + context + " " + odds + " " + match})
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply

def createProp(sport_key, text):
    start = (datetime.now() - timedelta(hours=48)).timestamp()
    end = datetime.now().timestamp()
    game = text.split(':')
    gameId = game[0]
    #print("game id: " + gameId)
    match = game[1]
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    try:
      newsArticles = ask.news.search_news("best prop bets for the text " + match, method='kw', return_type='dicts', n_articles=3, categories=["Sports"], premium=True, start_timestamp=int(start), end_timestamp=int(end)).as_dicts
      context = ""
      for article in newsArticles:
        context += article.summary
      #print(context)
    except:
      context = ""
    messages.append({"role": "user", "content": "Write a short article outlining the best individual player prop bets for the following matchup. List the odds and probability.  Give your best bet based on the context provided only mention play prop bets that are referenced in the context and mention the sportsbook.  The response should be in markdown format." + context + " " + match})
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply

def createParlay(sport_key, text):
    start = (datetime.now() - timedelta(hours=12)).timestamp()
    end = datetime.now().timestamp()
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    try:
      newsArticles = ask.news.search_news("same game parlay " + text, method='kw', return_type='dicts', n_articles=3, categories=["Sports"], premium=True, start_timestamp=int(start), end_timestamp=int(end)).as_dicts
      context = ""
      for article in newsArticles:
        context += article.summary
      #print(context)
    except:
      context = ""
    messages.append({"role": "user", "content": "Write a short article outlining the best same game parlay for the following matchup. List the odds and probability.  Give your best bet based on the context provided only mention parlays referenced in the context and include the sportsbook. Your response should be in markdown format." + context + " " + text})
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply

def topNews(sport_key):
    start = (datetime.now() - timedelta(hours=24)).timestamp()
    end = datetime.now().timestamp()
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": sport_key})
    try:
      newsArticles = ask.news.search_news(sport_key, method="kw", return_type='dicts', n_articles=3, categories=["Sports"], premium=True, start_timestamp=int(start), end_timestamp=int(end)).as_dicts
      context = ""
      for article in newsArticles:
        context += article.summary
      #print(context)
    except:
      context = ""
    messages.append({"role": "user", "content": "Write a funny, but accurate article briefly summarizing the various articles. Each article is enclosed in the <doc> </doc> tag.  Ignore redundant articles. Your response should be in markdown format." + context + " " + sport_key}),
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply


def createRecap(sport_key, text):
    start = (datetime.now() - timedelta(hours=48)).timestamp()
    end = datetime.now().timestamp()
    messages = []
    messages.append({"role": "system", "content": "You are the worlds best AI Sports Handicapper and sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    try:
        newsArticles = ask.news.search_news("final score of the following game " + text, method='kw', return_type='dicts', n_articles=3, categories=["Sports"], premium=True, start_timestamp=int(start), end_timestamp=int(end)).as_dicts
        context = ""
        for article in newsArticles:
          context += article.summary
    except:
        context = ""
    #print(context)
    #print(text)
    messages.append({"role": "user", "content": "Write a short, humorous article recapping the results following matchup include the score and highlights. Pay specific attention to the articles and only include information from context provided that is related to the game in question do not make up any details. Your response should be in markdown format. " + context + " " + text})
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply

def answerTrivia(text):
    messages = []
    messages.append({"role": "system", "content": "You are an AI sportswriter. You are smart, funny and accurate."})
    messages.append({"role": "user", "content": text})
    try:
        #context = ask.news.search_news("Answer the following sports trivia question" + text, method='kw', return_type='string', n_articles=10, categories=["Sports"]).as_string
        response = clientTavily.search(query=text, search_depth="advanced")
        context = [{"href": obj["url"], "body": obj["content"]} for obj in response.get("results", [])]
    except:
        context = ""
    context = str(context)
    #print(context)
    messages.append({"role": "user", "content": "Given the following context answer the sports trivia question at the end.  Be humorous but accurate.  If the question is not sports related, politely refuse to answer. Your response should be in markdown format." + context + " " + text})
    chat_response = chat_completion_request(messages)
    #reply = chat_response.choices[0].message.content + "\n" + random.choice(referral_links)
    reply = chat_response.choices[0].message.content
    #print(reply)
    return reply

async def get_sport(ctx: discord.AutocompleteContext):
  sport = ctx.options['sport']
  dataGames = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals&bookmakers=draftkings&oddsFormat=decimal")
  dataGames = dataGames.json()
  games = []
  for i in range(len(dataGames)):
      t = dataGames[i]['commence_time']
      utcTime = dtdt(int(t[0:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]), tzinfo=utc)
      esTime = utcTime.astimezone(ept)
      #games.append(dataGames[i]['home_team'] + " vs " + dataGames[i]['away_team'] + " " + str(esTime))
      homeTeam = dataGames[i]['home_team'].split()
      awayTeam = dataGames[i]['away_team'].split()
      game = dataGames[i]['id'] + ": " + dataGames[i]['home_team'] + " vs " + dataGames[i]['away_team'] + " " + str(esTime)
      #game = dataGames[i]['id'] + ": " + dataGames[i]['home_team'] + " vs " + dataGames[i]['away_team']
      game = game[:100]
      #print(game)
      games.append(game)
  return games

async def get_score(ctx: discord.AutocompleteContext):
  sport = ctx.options['sport']
  dataGames = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/scores/?daysFrom=1&apiKey={ODDS_API_KEY}")
  dataGames = dataGames.json()
  games = []
  for i in range(len(dataGames)):
      if dataGames[i]['completed'] == True:
          t = dataGames[i]['commence_time']
          utcTime = dtdt(int(t[0:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]), tzinfo=utc)
          esTime = utcTime.astimezone(ept)
          games.append(dataGames[i]['home_team'] + " vs " + dataGames[i]['away_team'] + " " + str(esTime))
  return games

@bot.event
async def on_ready():
    #bot.loop.create_task(gameLoop(bot))
    print(f"{bot.user} is ready and online!")

#async def gameLoop(bot):
#    while True:
#        sports = ['baseball_mlb','basketball_nba','icehockey_nhl','mma_mixed_martial_arts','basketball_wnba','soccer_usa_mls','rugby_league_nrl','americanfootball_cfl']
#        for sport in sports:
#            dataGames = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals&bookmakers=draftkings&oddsFormat=american")
#            #print("updated: " f"{sport}")
#            await asyncio.sleep(10)
#        await asyncio.sleep(900)

#@bot.slash_command(name="prediction", description="Up to date AI generated predictions on sporting events.")
#async def prediction_command(
#  ctx: discord.ApplicationContext,
#  sport: discord.Option(str, choices=sport_keys),
#  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_sport))
#):
#  await ctx.defer()
#  await ctx.respond((createMessage(f"{sport}", f"{game}"))[:2000])

@bot.slash_command(name="prediction", description="Up to date AI generated predictions on sporting events.")
async def prediction_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, choices=sport_keys),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_sport))
):
  await ctx.defer() 
  prediction = createMessage(f"{sport}", f"{game}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="",description=prediction, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

@bot.slash_command(name="props", description="Best Prop Bets.")
async def props_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, choices=sport_keys),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_sport))
):
  await ctx.defer()
  prop = createProp(f"{sport}", f"{game}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="https://record.revmasters.com/_8ejz3pKmFDuMKNOJN2Xw7mNd7ZgqdRLk/1/",description=prop, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

@bot.slash_command(name="samegameparlay", description="Best Same Game Parlay.")
async def samegameparlay_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, choices=sport_keys),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_sport))
):
  await ctx.defer()
  parlay = createParlay(f"{sport}", f"{game}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="https://record.revmasters.com/_8ejz3pKmFDuMKNOJN2Xw7mNd7ZgqdRLk/1/",description=parlay, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

@bot.slash_command(name="topnews", description="Latest news by sport.")
async def topnews_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, choices=leagues),
):
  await ctx.defer()
  news = topNews(f"{sport}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="https://record.revmasters.com/_8ejz3pKmFDuMKNOJN2Xw7mNd7ZgqdRLk/1/",description=news, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

@bot.slash_command(name="recap", description="Get highlights of recent matches.")
async def recap_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, choices=sport_keys),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_score))
):
  await ctx.defer()
  recap = createRecap(f"{sport}", f"{game}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="https://record.revmasters.com/_8ejz3pKmFDuMKNOJN2Xw7mNd7ZgqdRLk/1/",description=recap, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

@bot.slash_command(name="trivia", description="Ask me any anything sport related.")
async def trivia_command(
  ctx: discord.ApplicationContext,
  question: discord.Option(str)
):
  await ctx.defer()
  trivia = answerTrivia(f"{question}")[:2000]
  embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="https://record.revmasters.com/_8ejz3pKmFDuMKNOJN2Xw7mNd7ZgqdRLk/1/",description=trivia, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed.add_field(name='GPTSW Discord Server' ,value='[Click here to Join]( https://discord.gg/gBzTrbyybX )', inline=False)
  embed.add_field(name='Like GPTSportswriter?' ,value='[Click here to Donate]( https://buymeacoffee.com/normandmicP )', inline=False)
  embed.add_field(name='BetUS - 125% Bonus On Your First 3 Deposits' ,value='[Click here to Sign Up]( https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/ )', inline=False)
  await ctx.respond(embed=embed)

bot.run(os.environ.get('DISCORD_BOT_TOKEN')) # run the bot with the token

