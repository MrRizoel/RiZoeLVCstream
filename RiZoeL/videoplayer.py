import os
import re
import time
import ffmpeg
import asyncio
from os import path
from asyncio import sleep
from youtube_dl import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pytgcalls import GroupCallFactory
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, SESSION_NAME, BOT_USERNAME
from helpers.decorators import authorized_users_only
from helpers.filters import command


STREAM = {8}
VIDEO_CALL = {}


ydl_opts = {
        "format": "best",
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "videoformat": "mp4",
        "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)

app = Client(SESSION_NAME, API_ID, API_HASH)
group_call_factory = GroupCallFactory(app, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)


@Client.on_message(command(["vplay", f"vplay@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
async def vstream(client, m: Message):
    if 1 in STREAM:
        await m.reply_text("๐ **sorry, there's another video streaming right now**\n\nยป **wait for it to finish then try again!**")
        return

    media = m.reply_to_message
    if not media and not ' ' in m.text:
        await m.reply("๐บ **please reply to a video or live stream url or youtube url to stream the video!**")

    elif ' ' in m.text:
        msg = await m.reply_text("๐ **processing youtube url...**")
        text = m.text.split(' ', 1)
        url = text[1]
        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex,url)
        if match:
            await msg.edit("๐ **starting youtube streaming...**")
            try:
                info = ydl.extract_info(url, False)
                ydl.download([url])
                ytvid = path.join("downloads", f"{info['id']}.{info['ext']}")
            except Exception as e:
                await msg.edit(f"โ **youtube downloader error!** \n\n`{e}`")
                return
            await sleep(2)
            try:
                chat_id = m.chat.id
                group_call = group_call_factory.get_group_call()
                await group_call.join(chat_id)
                await group_call.start_video(ytvid)
                VIDEO_CALL[chat_id] = group_call
                await msg.edit((f"๐ก **started [youtube streaming]({url}) !\n\nยป join to video chat to watch the youtube stream.**"), disable_web_page_preview=True)
                try:
                    STREAM.remove(0)
                except:
                    pass
                try:
                    STREAM.add(1)
                except:
                    pass
            except Exception as e:
                await msg.edit(f"โ **something went wrong!** \n\nError: `{e}`")
        else:
            await msg.edit("๐ **starting live streaming...**")
            live = url
            chat_id = m.chat.id
            await sleep(2)
            try:
                group_call = group_call_factory.get_group_call()
                await group_call.join(chat_id)
                await group_call.start_video(live)
                VIDEO_CALL[chat_id] = group_call
                await msg.edit((f"๐ก **started [live streaming]({live}) !\n\nยป join to video chat to watch the live stream.**"), disable_web_page_preview=True)
                try:
                    STREAM.remove(0)
                except:
                    pass
                try:
                    STREAM.add(1)
                except:
                    pass
            except Exception as e:
                await msg.edit(f"โ **something went wrong!** \n\nError: `{e}`")

    elif media.video or media.document:
        msg = await m.reply_text("๐ฅ **downloading video...**\n\n๐ญ __this process will take quite a while depending on the size of the video.__")
        video = await client.download_media(media)
        chat_id = m.chat.id
        await sleep(2)
        try:
            group_call = group_call_factory.get_group_call()
            await group_call.join(chat_id)
            await group_call.start_video(video)
            VIDEO_CALL[chat_id] = group_call
            await msg.edit("๐ก **video streaming started!**\n\nยป **join to video chat to watch the video.**")
            try:
                STREAM.remove(0)
            except:
                pass
            try:
                STREAM.add(1)
            except:
                pass
        except Exception as e:
            await msg.edit(f"โ **something went wrong!** \n\nError: `{e}`")
    else:
        await m.reply_text("๐บ **please reply to a video or live stream url or youtube url to stream the video!**")
        return


@Client.on_message(command(["stop", f"stop@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def vstop(client, m: Message):
    chat_id = m.chat.id
    if 0 in STREAM:
        await m.reply_text("๐ **no active streaming at this time**\n\nยป start streaming by using /vplay command (reply to video/yt url/live url)")
        return
    try:
        await VIDEO_CALL[chat_id].stop()
        await m.reply_text("๐ด **streaming has ended !**\n\nโ __userbot has been disconnected from the video chat__")
        try:
            STREAM.remove(1)
        except:
            pass
        try:
            STREAM.add(0)
        except:
            pass
    except Exception as e:
        await m.reply_text(f"โ **something went wrong!** \n\nError: `{e}`")
