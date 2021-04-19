import google_service
import discord
import datetime
from discord.ext import commands

from decouple import config

app = commands.Bot(command_prefix='/')

calendar = google_service.get_calendar_service()


@app.command(aliases=['일정'])
async def get_events(ctx, maxResult=5):
    await ctx.send(f'가까운 일정 {maxResult}개를 가져오고 있습니다...')

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = calendar.events().list(calendarId='primary', timeMin=now,
                                           maxResults=maxResult, singleEvents=True,
                                           orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        await ctx.send('가까운 일정이 없습니다.')
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        embed = discord.Embed(title=event.get('summary'),
                              url=event.get('htmlLink'),
                              description=f'{start} ~ {end}\nid: {event.get("id")}')
        await ctx.send(embed=embed)

    await ctx.send('가져오기 완료!')


@app.command(aliases=['일정생성'])
async def create_event(ctx, summary, startdate, enddate, freq="DAILY", count=1):
    await ctx.send('일정 생성 중입니다...')

    event = {
        'summary': summary,
        'start': {
            'date': startdate,
            'timeZone': 'Asia/Seoul',
        },
        'end': {  # 종료 날짜
            'date': enddate,
            'timeZone': 'Asia/Seoul',
        },
        'recurrence': [  # 반복 지정
            f'RRULE:FREQ={freq};COUNT={count}'
        ],
    }

    event = calendar.events().insert(calendarId='primary', body=event).execute()

    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    embed = discord.Embed(title=event.get('summary'),
                          url=event.get('htmlLink'),
                          description=f'{start} ~ {end}\nid: {event.get("id")}')
    await ctx.send('일정을 생성하였습니다.', embed=embed)
    # await ctx.send(f'일정이 생성되었습니다: {event.get("htmlLink")}')


@app.event
async def on_ready():
    print(f'{app.user.name} 연결 성공')
    await app.change_presence(status=discord.Status.online, activity=None)


app.run(config('BOT_TOKEN'))
