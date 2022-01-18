import asyncio
import time
import heroku3

from ethon.FasterTg import upload_file, download_file
from ethon.telefunc import hbs

from main import *
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon import Button


def mention(*args):
    if len(args) == 1:
        event = args[0]
        return f'[{event.sender.first_name}](tg://user?id={event.sender_id})'
    return f'[{args[1]}](tg://user?id={args[0]})'


async def check_sub(user_id):
    try:
        sub = await bot(GetParticipantRequest(CHANNEL, user_id))
        status = sub.stringify()
        if 'left' in status:
            return False
        return True
    except UserNotParticipantError:
        return False


async def send_sub_request(event):
    markup = [[Button.url('🔗 VIEW THE CHANNEL', url=JOINCHAT_LINK)],
              [Button.inline('✅ CONFIRM', data='confirm')]]
    await event.respond('⚠️ Please, subscribe to the channel to use the bot', buttons=markup)


def get_buttons(user_id):
    if user_id == ADMIN:
        buttons = [
            [Button.text(RESTART_TEXT), Button.text(POST_TEXT)],
            [Button.text(USERS_COUNT_TEXT), Button.text(TOP_USERS_TEXT, resize=True)]
        ]
        return buttons
    return None


async def restart_heroku():
    if not HEROKU_API and HEROKU_APP:
        return False
    heroku = heroku3.from_key(HEROKU_API)
    bot_app = heroku.apps()[HEROKU_APP]
    bot_app.restart()
    return True


def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + " weeks ") if weeks else "")
        + ((str(days) + " days ") if days else "")
        + ((str(hours) + " hours ") if hours else "")
        + ((str(minutes) + " minutes ") if minutes else "")
        + ((str(seconds) + " seconds ") if seconds else "")
    )
    return tmp


async def progress(current, total, event, start, type_of_ps):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "**{0}{1}**\n`{2}%`\n\n".format(
            "■" * int(3 * percentage // 20),
            "□" * (15 - int(3 * percentage // 20)),
            round(percentage, 1),
        )
        tmp = (
            progress_str
            + "**Uploaded:** {0} of {1}\n**Speed:** {2}/s\n**Time left:** {3}".format(
                hbs(current),
                hbs(total),
                hbs(speed),
                time_formatter(time_to_completion),
            )
        )
        await event.edit("{}\n\n{}".format(type_of_ps, tmp))


async def fast_upload(file, name, upload_time, client, event, msg):
    with open(file, "rb") as f:
        result = await upload_file(
            client=client,
            file=f,
            filename=name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    event,
                    upload_time,
                    msg,
                ),
            ),
        )
    return result


def get_resolution_buttons(resolutions):
    buttons = []
    for i in range(0, len(resolutions), 3):
        buttons_3 = [Button.inline(res, data=res) for res in resolutions[i:i+3]]
        if len(buttons_3) < 3:
            buttons_3.append(Button.inline('audio', data='audio'))
        buttons.append(buttons_3)
    if len(resolutions) % 3 == 0:
        buttons.append([Button.inline('audio', data='audio')])
    return buttons
