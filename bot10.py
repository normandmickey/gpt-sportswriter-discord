import asyncio
import discord
import functools
import pytz
import time

from config_runtime import DISCORD_BOT_TOKEN, HTTP_TIMEOUT, ODDS_API_KEY, http, logger
from analytics import ensure_analytics_table, log_command_event
from autocomplete_helpers import autocomplete_league, autocomplete_sport_label, build_sport_maps, get_score, get_sport
from content_generators import answerTrivia, createMessage, createParlay, createProp, createRecap, topNews
from embeds import build_response_embed
from topgg_helpers import post_topgg_stats

bot = discord.Bot()

ept = pytz.timezone('US/Eastern')
utc = pytz.utc
# str format
#fmt = '%Y-%m-%d %H:%M:%S %Z%z'
fmt = '%Y-%m-%d'
referral_links = ["BetUS - 125% Sign Up Bonus! - https://record.revmasters.com/_8ejz3pKmFDsdHrf4TDP9mWNd7ZgqdRLk/1/","https://cash.app The CashApp is the best way to send money for free. Enter the code WPVJMVS when you sign up and we'll send you $5 when you try it.","https://www.draftkings.com/r/normandmickey","Get $50 on FanDuel Sportsbook in Bonus Bets! Terms apply. Make sure to use my invite link! https://fndl.co/jcafr4b","https://www.ny.betmgm.com/en/mobileportal/invitefriendssignup?invID=5387173","https://caesars.com/sportsbook-and-casino/referral?AR=RAF-BEG-AAV","https://fanatics.onelink.me/5kut/xxyt95qs"]
#referral_links = ["BetUS - 125% Sign Up Bonus! - https://tinyurl.com/GPTSW2","https://cash.app The CashApp is the best way to send money for free. Enter the code WPVJMVS when you sign up and we'll send you $5 when you try it."]
#referral_links = ["BetUS - 125% Sign Up Bonus! - https://record.revmasters.com/_8ejz3pKmFDtD3TEmsPWI0WNd7ZgqdRLk/1/"]

dataSportKeys = http.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}", timeout=HTTP_TIMEOUT)
dataSportKeys.raise_for_status()
dataSportKeys = dataSportKeys.json()

sport_labels = []
leagues = []
label_to_key = {}

includedSports = ['American Football',
                  'Aussie Rules',
                  'Baseball',
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
sport_labels, leagues, label_to_key = build_sport_maps(dataSportKeys, includedSports, excludedLeagues)



async def _topgg_stats_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        post_topgg_stats(bot)
        await asyncio.sleep(1800)


@bot.event
async def on_ready():
    ensure_analytics_table()
    logger.info("%s is ready and online! Installed in %s guild(s).", bot.user, len(bot.guilds))
    post_topgg_stats(bot, force=True)
    if not getattr(bot, '_topgg_loop_started', False):
        bot._topgg_loop_started = True
        bot.loop.create_task(_topgg_stats_loop())


@bot.event
async def on_guild_join(guild):
    logger.info("Joined guild %s (%s). Installed in %s guild(s).", guild.name, guild.id, len(bot.guilds))
    post_topgg_stats(bot, force=True)


@bot.event
async def on_guild_remove(guild):
    logger.info("Removed from guild %s (%s). Installed in %s guild(s).", guild.name, guild.id, len(bot.guilds))
    post_topgg_stats(bot, force=True)

#async def gameLoop(bot):
#    while True:
#        sports = ['baseball_mlb','basketball_nba','icehockey_nhl','mma_mixed_martial_arts','basketball_wnba','soccer_usa_mls','rugby_league_nrl','americanfootball_cfl']
#        for sport in sports:
#            dataGames = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals&bookmakers=draftkings&oddsFormat=american")
#            #print("updated: " f"{sport}")
#            await asyncio.sleep(10)
#        await asyncio.sleep(900)

@bot.slash_command(name="prediction", description="Up to date AI generated predictions on sporting events.")
async def prediction_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(autocomplete_sport_label, sport_labels=sport_labels))),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(get_sport, utc=utc, ept=ept, label_to_key=label_to_key)))
):
  await ctx.defer()
  started = time.perf_counter()
  source = 'generated'
  prediction = createMessage(label_to_key.get(sport, sport), f"{game}", utc, ept)[:2000]
  image_url = None
  if 'Odd$mith Best Bet:' in prediction:
      source = 'oddsmith_pick'
  if '\n\nImage: ' in prediction:
      prediction, image_url = prediction.rsplit('\n\nImage: ', 1)
      image_url = image_url.strip() or None
  embed = build_response_embed(prediction)
  if image_url:
      embed.set_image(url=image_url)
  await ctx.respond(embed=embed)
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='prediction', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), sport_label=sport, game_label=game, source=source, success=True, duration_ms=duration_ms)

@bot.slash_command(name="props", description="Best Prop Bets.")
async def props_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(autocomplete_sport_label, sport_labels=sport_labels))),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(get_sport, utc=utc, ept=ept, label_to_key=label_to_key)))
):
  await ctx.defer()
  started = time.perf_counter()
  prop = createProp(label_to_key.get(sport, sport), f"{game}", utc, ept)[:2000]
  #embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="",description=prediction, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed = build_response_embed(prop)
  await ctx.respond(embed=embed)
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='props', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), sport_label=sport, game_label=game, source='generated', success=True, duration_ms=duration_ms)

@bot.slash_command(name="samegameparlay", description="Best Same Game Parlay.")
async def samegameparlay_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(autocomplete_sport_label, sport_labels=sport_labels))),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(get_sport, utc=utc, ept=ept, label_to_key=label_to_key)))
):
  await ctx.defer()
  started = time.perf_counter()
  parlay = createParlay(label_to_key.get(sport, sport), f"{game}")[:2000]
  #embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="",description=prediction, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed = build_response_embed(parlay)
  await ctx.respond(embed=embed)
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='samegameparlay', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), sport_label=sport, game_label=game, source='generated', success=True, duration_ms=duration_ms)

@bot.slash_command(name="topnews", description="Latest news by sport.")
async def topnews_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(autocomplete_league, leagues=leagues))),
):
  await ctx.defer()
  started = time.perf_counter()
  news = topNews(f"{sport}")[:2000]
  #embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="",description=prediction, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed = build_response_embed(news)
  await ctx.respond(embed=embed)
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='topnews', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), sport_label=sport, source='generated', success=True, duration_ms=duration_ms)

@bot.slash_command(name="recap", description="Get highlights of recent matches.")
async def recap_command(
  ctx: discord.ApplicationContext,
  sport: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(autocomplete_sport_label, sport_labels=sport_labels))),
  game: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(functools.partial(get_score, utc=utc, ept=ept, label_to_key=label_to_key)))
):
  await ctx.defer()
  started = time.perf_counter()
  recap = createRecap(label_to_key.get(sport, sport), f"{game}", utc, ept).strip()
  recap = recap[:3800]
  recap_parts = [recap]
  if 'https://oddsmith.net' not in recap:
      recap_parts.extend(['', 'More picks: https://oddsmith.net'])
  await ctx.respond('\n'.join(recap_parts).strip())
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='recap', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), sport_label=sport, game_label=game, source='generated', success=True, duration_ms=duration_ms)

@bot.slash_command(name="trivia", description="Ask me any anything sport related.")
async def trivia_command(
  ctx: discord.ApplicationContext,
  question: discord.Option(str)
):
  await ctx.defer()
  started = time.perf_counter()
  trivia = answerTrivia(f"{question}")[:2000]
  #embed=discord.Embed(title="BetUS - 125% Sign Up Bonus!", url="",description=prediction, image="https://media.revmasters.com/uploads/002xnbaseason24-970x250-aff.gif")
  embed = build_response_embed(trivia)
  await ctx.respond(embed=embed)
  duration_ms = int((time.perf_counter() - started) * 1000)
  log_command_event(command_name='trivia', guild_id=str(ctx.guild.id) if ctx.guild else None, channel_id=str(ctx.channel.id) if ctx.channel else None, user_id=str(ctx.user.id), username=str(ctx.user), source='generated', success=True, duration_ms=duration_ms)

@bot.slash_command(name="listservers", description="List Servers")
async def bot_members(ctx):  
  guild = ctx.guild
  bot_members = []  
  get_bot_members = ([m for m in guild.members if m.bot])  
  for bot in get_bot_members:  
    bot_members.append(bot.name)  
 
  await ctx.send(', '.join(bot_members))

bot.run(DISCORD_BOT_TOKEN) # run the bot with the token

