import time
from os import remove
import requests
from ethon.pyfunc import bash
from telethon import events, Button
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from ethon.telefunc import hbs

from main.utils import restart_heroku, check_sub, send_sub_request, get_buttons, mention, fast_upload
from main.database import Database
from main import bot, ADMIN, RESTART_TEXT, POST_TEXT, USERS_COUNT_TEXT, CANCEL_TEXT, TOP_USERS_TEXT, GROUP_ID, BOT_UN

db = Database()
WAITING_POST = []


@bot.on(events.NewMessage(incoming=True, pattern="/start", func=lambda e: e.is_private))
async def start(event):
    if event.sender_id in WAITING_POST:
        WAITING_POST.remove(event.sender_id)
    await event.respond(f"👋 Hi {mention(event)}!\n🤖 I'm **Video Convertor**\n"
                        f"🎞 Just send me a video and I convert it to audio format",
                        buttons=get_buttons(event.sender_id))


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def add_user_db(event):
    user_id = event.sender_id
    is_user_exist_db = await db.is_user_exist(user_id)
    if not is_user_exist_db:
        await bot.send_message(GROUP_ID, f'{mention(event)} started using **the bot**')
        await db.add_user(user_id)


@bot.on(events.NewMessage(incoming=True, pattern=CANCEL_TEXT))
async def cancel_operation(event):
    if event.sender_id in WAITING_POST:
        WAITING_POST.remove(event.sender_id)
    await event.respond('**❌ Canceled**', buttons=get_buttons(event.sender_id))


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def get_youtube_link(event):
    try:
        link = event.message.message
        streams = YouTube(link).streams
        thumbnail_url = YouTube(link).thumbnail_url
        thumb = thumbnail_url.split('/')[-1]
        response = requests.get(thumbnail_url)
        file = open(thumb, 'wb')
        file.write(response.content)
        file.close()
        videos = streams.filter(adaptive=True).filter(only_video=True).order_by('resolution')
        audios = streams.filter(only_audio=True)
        for video in videos:
            file = video.download()
            print(file)
            await bot.send_file(event.sender_id, file, thumb=thumb, supports_streaming=True)
        for audio in audios:
            await event.respond(f'{str(audio)} {hbs(audio.filesize)}')
    except RegexMatchError:
        pass


@bot.on(events.NewMessage(incoming=True, from_users=[ADMIN], pattern=RESTART_TEXT))
async def restart(event):
    result = await restart_heroku()
    if result:
        await event.respond('**✔️ Restarted app**')
    else:
        await event.respond('**❌ An error occurred!**')


@bot.on(events.NewMessage(incoming=True, pattern=USERS_COUNT_TEXT))
async def get_users_count(event):
    if not await check_sub(event.sender_id):
        await send_sub_request(event)
        return
    message = await event.respond('**👤 Counting total users ...**')
    count = await db.total_users_count()
    await message.edit(f'`👤 Total users {count}`')


@bot.on(events.NewMessage(incoming=True, pattern=TOP_USERS_TEXT))
async def get_converts_count(event):
    if not await check_sub(event.sender_id):
        await send_sub_request(event)
        return
    message = await event.respond('**📥 Loading users data ...**')
    top_users = await db.get_downloads_leaders()
    text = f'**{TOP_USERS_TEXT}**\n\n'
    for num, user_info in enumerate(top_users):
        user = await bot.get_entity(user_info['id'])
        text += f"**{num + 1}.** {mention(user.id, user.first_name)} - " \
                f"`{user_info['downloads']}` downloads\n"
    await message.edit(text)


@bot.on(events.NewMessage(incoming=True, from_users=[ADMIN], func=lambda e: e.sender_id in WAITING_POST))
async def get_post(event):
    message = await event.respond('**👤 Counting total users ...**')
    count = await db.total_users_count()
    await message.edit(f'`👤 Total users {count}`')
    post = event.message
    all_users = await db.get_users()
    sent = 0
    failed = 0
    text = "**👤 Total users in the database** `{0}`\n**📤 SENT:** `{1}`\n**🚫 FAILED:** `{2}`"
    async for user in all_users:
        userid = user.get('id', None)
        try:
            await bot.send_message(userid, post)
            sent += 1
            await message.edit(text.format(count, sent, failed))
        except Exception as e:
            bot_user = await bot.get_entity(userid)
            await bot.send_message(GROUP_ID, f'**❌ {mention(bot_user.id, bot_user.first_name)} '
                                             f'was removed from the database**\n\n**⚠️ Reason:** {str(e)}')
            failed += 1
            await db.delete_user(userid)
            await message.edit(text.format(count, sent, failed))
    await message.delete()
    await event.respond("**✅ COMPLETE!**\n\n" + text.format(count, sent, failed),
                        buttons=get_buttons(event.sender_id))
    WAITING_POST.remove(event.sender_id)


@bot.on(events.NewMessage(incoming=True, from_users=[ADMIN], pattern=POST_TEXT))
async def post_to_users(event):
    await event.respond(f'**📩 Send me a post**', buttons=[[Button.text(CANCEL_TEXT, resize=True)]])
    WAITING_POST.append(event.sender_id)


@bot.on(events.CallbackQuery(pattern='confirm'))
async def confirm(event):
    status = await check_sub(event.sender_id)
    if status:
        await event.delete()
        group = await bot.get_entity(GROUP_ID)
        await bot.send_message(group, f'{mention(event)} joined **the channel**')
        await event.respond('**✅ Now you can use the bot. Send me a video to use the bot**\n',
                            buttons=get_buttons(event.sender_id))
    else:
        await event.answer("🚫 You aren't a member of the channel", alert=True)


print('🤖 Bot started working ...')

if __name__ == '__main__':
    bot.run_until_disconnected()
