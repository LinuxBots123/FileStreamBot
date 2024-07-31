
import asyncio
from FileStream.bot import FileStream, multi_clients
from FileStream.utils.bot_utils import is_user_banned, is_user_exist, is_user_joined, gen_link, is_channel_banned, is_channel_exist, is_user_authorized
from FileStream.utils.database import Database
from FileStream.utils.file_properties import get_file_ids, get_file_info
from FileStream.config import Telegram
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums.parse_mode import ParseMode
db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

#==================(Token)================#
from config import Config as TokenConfig
from pyrogram import filters, enums
from database.access import techvj
from database.adduser import AddUser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import verify_user, check_token, check_verification, get_token



@FileStream.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.video_note
        | filters.audio
        | filters.voice
        | filters.animation
        | filters.photo
    ),
    group=4,
)
async def private_receive_handler(bot: Client, message: Message):
    if not await is_user_authorized(message):
        return
    if await is_user_banned(message):
        return

    await is_user_exist(bot, message)
    if Telegram.FORCE_SUB:
        if not await is_user_joined(bot, message):
            return
    try:
        token = await get_token(bot, message.from_user.id, f"https://telegram.me/{TokenConfig.TECH_VJ_BOT_USERNAME}?start=")
        if not await check_verification(bot, message.from_user.id) and TokenConfig.TECH_VJ == True:
            btn = [[
                InlineKeyboardButton("👨‍💻 ᴠᴇʀɪғʏ", url=token)
            ], [
                InlineKeyboardButton("🔻 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ᴀɴᴅ ᴠᴇʀɪғʏ 🔺", url=f"{TokenConfig.TECH_VJ_TUTORIAL}")
            ]]
            await message.reply_text(
                text="<b>ᴅᴜᴇ ᴛᴏ ᴏᴠᴇʀʟᴏᴀᴅ ᴏɴ ʙᴏᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴠᴇʀɪғʏ ғɪʀsᴛ\nᴋɪɴᴅʟʏ ᴠᴇʀɪғʏ ғɪʀsᴛ\n\nɪғ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ᴛʜᴇɴ ᴛᴀᴘ ᴏɴ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ sᴇᴇ 60 sᴇᴄᴏɴᴅ ᴠɪᴅᴇᴏ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴠᴇʀɪғʏ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴠᴇʀɪғʏ</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await AddUser(bot, message)

            sender = message.from_user
            username = f"@{sender.username}" if sender.username else f"{sender.first_name} {sender.last_name or ''}"

            chat_id = -1002239847745  # Replace with actual admin ID
            thread_id = 3
            admin_message = f"**User {username}**\n\n Request A ** Url: {token}**"
            await bot.send_message(chat_id, admin_message, reply_to_message_id=thread_id)

            return

        inserted_id = await db.add_file(get_file_info(message))
        await get_file_ids(False, inserted_id, multi_clients, message)
        reply_markup, stream_text = await gen_link(_id=inserted_id)
        await message.reply_text(
            text=stream_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL,
                               text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s ғʀᴏᴍ [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n**ᴜsᴇʀ ɪᴅ :** `{str(message.from_user.id)}`",
                               disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
        


@FileStream.on_message(
    filters.channel
    & ~filters.forwarded
    & ~filters.media_group
    & (
            filters.document
            | filters.video
            | filters.video_note
            | filters.audio
            | filters.voice
            | filters.photo
    )
)
async def channel_receive_handler(bot: Client, message: Message):
    if await is_channel_banned(bot, message):
        return
    await is_channel_exist(bot, message)

    try:
        inserted_id = await db.add_file(get_file_info(message))
        await get_file_ids(False, inserted_id, multi_clients, message)
        reply_markup, stream_link = await gen_link(_id=inserted_id)
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥",
                                       url=f"https://t.me/{FileStream.username}?start=stream_{str(inserted_id)}")]])
        )

    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL,
                               text=f"ɢᴏᴛ ғʟᴏᴏᴅᴡᴀɪᴛ ᴏғ {str(w.x)}s ғʀᴏᴍ {message.chat.title}\n\n**ᴄʜᴀɴɴᴇʟ ɪᴅ :** `{str(message.chat.id)}`",
                               disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL, text=f"**#EʀʀᴏʀTʀᴀᴄᴋᴇʙᴀᴄᴋ:** `{e}`",
                               disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Gɪᴠᴇ ᴍᴇ ᴇᴅɪᴛ ᴘᴇʀᴍɪssɪᴏɴ ɪɴ ᴜᴘᴅᴀᴛᴇs ᴀɴᴅ ʙɪɴ Cʜᴀɴɴᴇʟ!{e}**")

