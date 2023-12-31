# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_filter")

import os
import re
import asyncio

from telegraph import upload_file as uf
from telethon.tl.types import User
from telethon.utils import pack_bot_file_id

from pyUltroid.dB.filter_db import add_filter, get_filter, list_filter, rem_filter
from pyUltroid.fns.tools import create_tl_btn, format_btn, get_msg_button

from telethon import events
from telethon.sync import TelegramClient

from ._inline import something

# Function to retrieve messages with a space delay until condition command is used
async def retrieve_messages_with_space(chat_id, max_messages=7, condition_command="/remfilter", space_delay=2):
    messages = []
    count = 0

    while count < max_messages:
        msg = await ultroid_bot.get_messages(chat_id, limit=1)
        messages.append(msg)
        await asyncio.sleep(space_delay)

        # Check if the message has text before accessing it
        if msg.text and condition_command and condition_command.lower() in msg.text.lower():
            break  # Exit the loop when the condition command is found

        count += 1

    return messages

@ultroid_bot.on(events.NewMessage)
async def filter_func(e):
    if isinstance(e.sender, User) and e.sender.bot:
        return
    xx = (e.text).lower()
    chat = e.chat_id
    if x := get_filter(chat):
        for c in x:
            pat = r"( |^|[^\w])" + re.escape(c) + r"( |$|[^\w])"
            if re.search(pat, xx):
                if k := x.get(c):
                    msg = k["msg"]
                    media = k["media"]
                    if k.get("button"):
                        btn = create_tl_btn(k["button"])
                        return await something(e, msg, media, btn)
                    await e.reply(msg, file=media)

@ultroid_bot.on(events.NewMessage(pattern=r"addfilter( (.*)|$)"))
async def af(e):
    wrd = (e.pattern_match.group(1).strip()).lower()

    # Retrieve 7 messages until "/remfilter" command is used
    replied_messages = await retrieve_messages_with_space(e.chat_id, max_messages=7, condition_command="/remfilter", space_delay=2)

    for wt in replied_messages:
        # Process each retrieved message as needed
        if wt.media:
            # Process media messages
            wut = mediainfo(wt.media)
            if wut.startswith(("pic", "gif")):
                dl = await wt.download_media()
                variable = uf(dl)
                m = f"https://graph.org{variable[0]}"
            elif wut == "video":
                if wt.media.document.size > 8 * 1000 * 1000:
                    return await e.reply("Video size is too large.", time=5)
                dl = await wt.download_media()
                variable = uf(dl)
                os.remove(dl)
                m = f"https://graph.org{variable[0]}"
            else:
                m = pack_bot_file_id(wt.media)
            if wt.text:
                txt = wt.text
                if not btn:
                    txt, btn = get_msg_button(wt.text)
                add_filter(e.chat_id, wrd, txt, m, btn)
            else:
                add_filter(e.chat_id, wrd, None, m, btn)
        else:
            txt = wt.text
            if not btn:
                txt, btn = get_msg_button(wt.text)
            add_filter(e.chat_id, wrd, txt, None, btn)

    await e.reply(get_string("flr_4").format(wrd))
    ultroid_bot.add_handler(filter_func, events.NewMessage())

@ultroid_bot.on(events.NewMessage(pattern=r"remfilter( (.*)|$)"))
async def rf(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    chat = e.chat_id
    if not wrd:
        return await e.reply(get_string("flr_3"))
    rem_filter(int(chat), wrd)
    await e.reply(get_string("flr_5").format(wrd))

@ultroid_bot.on(events.NewMessage(pattern=r"listfilter$"))
async def lsnote(e):
    if x := list_filter(e.chat_id):
        sd = "Filters Found In This Chats Are\n\n"
        return await e.reply(sd + x)
    await e.reply(get_string("flr_6"))

ultroid_bot.run_until_disconnected()
