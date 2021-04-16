import google_service
import discord
import datetime
from discord.ext import commands

from decouple import config

app = commands.Bot(command_prefix='/')

calendar = google_service.get_calendar_service()


@app.command(aliases=['일정'])
async def get_events(ctx):
    await ctx.send('Getting the upcoming 10 events. Wait...')

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = calendar.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        await ctx.send('가까운 일정이 없습니다.')
        return

    result_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result_list.append(f'```{start} {event["summary"]}```')

    await ctx.send('\n'.join(result_list))


@app.event
async def on_ready():
    print(f'{app.user.name} 연결 성공')
    await app.change_presence(status=discord.Status.online, activity=None)


app.run(config('BOT_TOKEN'))
