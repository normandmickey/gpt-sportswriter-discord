import discord


def build_response_embed(body):
    embed = discord.Embed(
        title="GPT SportsWriter by Odd$mith",
        url="https://oddsmith.net",
        description=body,
    )
    embed.add_field(
        name='More picks',
        value='[Visit Odd$mith](https://oddsmith.net)',
        inline=False,
    )
    embed.add_field(
        name='Get the app',
        value='[Odd$mith for Android - free on Google Play](https://play.google.com/store/apps/details?id=net.oddsmith.app)',
        inline=False,
    )
    return embed
