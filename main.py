import os
import json
import asyncio
import discord
from discord.ext import slash
from discord.ext.slash import _Route

SRCDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SRCDIR)

# directly ripped from https://github.com/RemyK888/discord-together/blob/main/src/DiscordTogether.js#L4-L15
APPS = {
    'YouTube': '880218394199220334',
    'YouTube (Dev)': '880218832743055411',
    'Poker': '755827207812677713',
    'Betrayal': '773336526917861400',
    'Fishing': '814288819477020702',
    'Chess': '832012774040141894',
    'Chess (Dev)': '832012586023256104',
    'LetterTile': '879863686565621790',
    'WordSnack': '879863976006127627',
    'DoodleCrew': '878067389634314250',
}

with open('config.json') as f:
    CONFIG = json.load(f)

client = slash.SlashBot(
    loop=asyncio.SelectorEventLoop(),
    description='Start various "Together" activities',
    command_prefix='/',
    help_command=None,
    activity=discord.Activity(type=discord.ActivityType.watching, name='/'),
    debug_guild=CONFIG.get('guild_id', None),
    resolve_not_fetch=False,
    fetch_if_not_get=True,
)

async def send_error(method, msg):
    await method(embed=discord.Embed(
        title='Error',
        description=msg,
        color=0xff0000
    ), ephemeral=True)

channel_opt = slash.Option(
    'The voice channel to start in.',
    slash.ApplicationCommandOptionType.CHANNEL)
type_opt = slash.Option(
    'The type of "together" to start.', name='type',
    choices=APPS.keys())

@client.slash_cmd()
async def start(
    ctx: slash.Context,
    channel: channel_opt = None,
    together: type_opt = 'YouTube'
):
    """Start something Together!"""
    name, together = together, APPS[together]
    if channel is None:
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await send_error(ctx.respond, "No channel specified and you're not in one")
            return
        channel = ctx.author.voice.channel
    route = _Route('POST', f'/channels/{channel.id}/invites')
    data = {
        'max_age': 86400, 'max_uses': 0,
        'target_application_id': together,
        'target_type': 2, 'temporary': False, 'validate': None
    }
    try:
        code = (await client.http.request(route, json=data))['code']
    except discord.Forbidden:
        await send_error(ctx.respond, f'Unable to start activity in {channel.mention}')
        return
    await ctx.respond(embed=discord.Embed(
        description=f'[Join {name}!](https://discord.gg/{code})'))

@client.slash_cmd()
async def invite(ctx: slash.Context):
    """Invite this bot to your server."""
    await ctx.respond(CONFIG['invite'])

async def wakeup():
    while 1:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.close()
            return

client.loop.create_task(wakeup())
client.run(CONFIG['token'])
