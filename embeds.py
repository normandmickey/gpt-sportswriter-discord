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
    return embed
