import logging
import math
from FileStream import __version__
from FileStream.bot import FileStream
from FileStream.server.exceptions import FIleNotFound
from FileStream.utils.bot_utils import gen_linkx, verify_user
from FileStream.config import Telegram
from FileStream.utils.database import Database
from FileStream.utils.translation import LANG, BUTTON
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums.parse_mode import ParseMode
import asyncio

#=====================(Token)================#
from utils import verify_user, check_token
from database.adduser import AddUser


db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

@FileStream.on_message(filters.command('start') & filters.private)
async def start(bot: Client, message: Message):
  #  if not await verify_user(bot, message):
     #   return
    usr_cmd = message.text.split("_")[-1]

    if usr_cmd == "/start":
        if Telegram.START_PIC:
            await message.reply_photo(
                photo=Telegram.START_PIC,
                caption=LANG.START_TEXT.format(message.from_user.mention, FileStream.username),
                parse_mode=ParseMode.HTML,
                reply_markup=BUTTON.START_BUTTONS
            )
        else:
            await message.reply_text(
                text=LANG.START_TEXT.format(message.from_user.mention, FileStream.username),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=BUTTON.START_BUTTONS
            )
    else:
        if "verify" in message.text:
            try:
                update = message
                data = update.command[1]
                if data.split("-", 1)[0] == "verify":
                    userid = data.split("-", 2)[1]
                    token = data.split("-", 3)[2]
                    if str(update.from_user.id) != str(userid):
                        return await update.reply_text(
                            text="<b>ᴇxᴘɪʀᴇᴅ ʟɪɴᴋ ᴏʀ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ !</b>",
                            protect_content=True
                        )
                    is_valid = await check_token(bot, userid, token)
                    if is_valid:
                        await update.reply_text(
                            text=f"<b>ʜᴇʟʟᴏ {update.from_user.mention} 👋,\nʏᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\n\nɴᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴜʀʟ ᴜᴘʟᴏᴀᴅɪɴɢ ᴛɪʟʟ ᴛᴏᴅᴀʏ ᴍɪᴅɴɪɢʜᴛ.</b>",
                            protect_content=True
                        )
                        await verify_user(bot, userid, token)
                        sender = update.from_user
                        username = f"@{sender.username}" if sender.username else f"{sender.first_name} {sender.last_name or ''}"
                        # Send message to the bot admin or log channel about the verification
                        chat_id = -1002273374091  # Replace with actual admin ID
                        thread_id = 4965
                        admin_message = f"**User {username}**\nverified access with \n**URL: {data}**"
                        await bot.send_message(chat_id, admin_message, reply_to_message_id=thread_id)
                    else:
                        return await update.reply_text(
                            text="<b>ᴇxᴘɪʀᴇᴅ ʟɪɴᴋ ᴏʀ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ !</b>",
                            protect_content=True
                        )
            except Exception as e:
                await message.reply_text("Something Went Wrong")
                logging.error(e)
        elif "stream_" in message.text:
            try:
                file_check = await db.get_file(usr_cmd)
                file_id = str(file_check['_id'])
                if file_id == usr_cmd:
                    reply_markup, stream_text = await gen_linkx(m=message, _id=file_id,
                                                                name=[FileStream.username, FileStream.fname])
                    await message.reply_text(
                        text=stream_text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                        reply_markup=reply_markup,
                        quote=True
                    )
            except FIleNotFound as e:
                await message.reply_text("File Not Found")
            except Exception as e:
                await message.reply_text("Something Went Wrong")
                logging.error(e)
        elif "file_" in message.text:
            try:
                file_check = await db.get_file(usr_cmd)
                db_id = str(file_check['_id'])
                file_id = file_check['file_id']
                file_name = file_check['file_name']
                if db_id == usr_cmd:
                    filex = await message.reply_cached_media(file_id=file_id, caption=f'**{file_name}**')
                    await asyncio.sleep(3600)
                    try:
                        await filex.delete()
                        await message.delete()
                    except Exception:
                        pass
            except FIleNotFound as e:
                await message.reply_text("**File Not Found**")
            except Exception as e:
                await message.reply_text("Something Went Wrong")
                logging.error(e)
        else:
            await message.reply_text(f"**Invalid Command**")

@FileStream.on_message(filters.private & filters.command(["about"]))
async def start(bot, message):
    
    if Telegram.START_PIC:
        await message.reply_photo(
            photo=Telegram.START_PIC,
            caption=LANG.ABOUT_TEXT.format(FileStream.fname, __version__),
            parse_mode=ParseMode.HTML,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )
    else:
        await message.reply_text(
            text=LANG.ABOUT_TEXT.format(FileStream.fname, __version__),
            disable_web_page_preview=True,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )

@FileStream.on_message((filters.command('help')) & filters.private)
async def help_handler(bot, message):
    
    if Telegram.START_PIC:
        await message.reply_photo(
            photo=Telegram.START_PIC,
            caption=LANG.HELP_TEXT.format(Telegram.OWNER_ID),
            parse_mode=ParseMode.HTML,
            reply_markup=BUTTON.HELP_BUTTONS
        )
    else:
        await message.reply_text(
            text=LANG.HELP_TEXT.format(Telegram.OWNER_ID),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=BUTTON.HELP_BUTTONS
        )

# ---------------------------------------------------------------------------------------------------

@FileStream.on_message(filters.command('files') & filters.private)
async def my_files(bot: Client, message: Message):
    
    user_files, total_files = await db.find_files(message.from_user.id, [1, 10])

    file_list = []
    async for x in user_files:
        file_list.append([InlineKeyboardButton(x["file_name"], callback_data=f"myfile_{x['_id']}_{1}")])
    if total_files > 10:
        file_list.append(
            [
                InlineKeyboardButton("◄", callback_data="N/A"),
                InlineKeyboardButton(f"1/{math.ceil(total_files / 10)}", callback_data="N/A"),
                InlineKeyboardButton("►", callback_data="userfiles_2")
            ],
        )
    if not file_list:
        file_list.append(
            [InlineKeyboardButton("ᴇᴍᴘᴛʏ", callback_data="N/A")],
        )
    file_list.append([InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")])
    await message.reply_photo(photo=Telegram.FILE_PIC,
                              caption="Total files: {}".format(total_files),
                              reply_markup=InlineKeyboardMarkup(file_list))
