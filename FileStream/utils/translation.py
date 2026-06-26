from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FileStream.config import Telegram

class LANG(object):

    START_TEXT = """
<b>👋 Hᴇʏ, </b>{}\n 
<b>I'ᴍ ᴀ Pᴇʀsᴏɴᴀʟ & Cʟᴇᴀɴ Fɪʟᴇ Sᴛʀᴇᴀᴍ & Dɪʀᴇᴄᴛ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴏʀ Bᴏᴛ</b>\n
<b>Sᴇɴᴅ ᴍᴇ ᴀɴʏ ғɪʟᴇ ᴏʀ ᴍᴇᴅɪᴀ ᴛᴏ ɢᴇᴛ ᴀ ᴅɪʀᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ!</b>\n
<b>🤖 @{}</b>
<b>👑 Mᴀɪɴᴛᴀɪɴᴇᴅ Bʏ : @cryvex4</b>\n"""

    HELP_TEXT = """
<b>📖 Hᴏᴡ ᴛᴏ Usᴇ:</b>
<b>- Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴅᴏᴄᴜᴍᴇɴᴛ, ᴠɪᴅᴇᴏ, ᴏʀ ᴍᴇᴅɪᴀ ғɪʟᴇ</b>
<b>- I ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅɪʀᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ</b>
<b>- Yᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴄʜᴀɴɴᴇʟs ғᴏʀ ᴀᴜᴛᴏ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛɪᴏɴ</b>"""

    ABOUT_TEXT = """
<b>⚜ Bᴏᴛ Nᴀᴍᴇ : {}</b>
<b>✦ Vᴇʀsɪᴏɴ : {}</b>
<b>✦ Tʏᴘᴇ : Pᴇʀsᴏɴᴀʟ Cʟᴇᴀɴ Sᴛʀᴇᴀᴍ Bᴏᴛ</b>
<b>👑 Oᴡɴᴇʀ : @cryvex4</b>
"""

    STREAM_TEXT = """
<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n
<b>📂 Fɪʟᴇ Nᴀᴍᴇ :</b> <b>{}</b>
<b>📦 Fɪʟᴇ Sɪᴢᴇ :</b> <code>{}</code>\n
<b>📥 Dɪʀᴇᴄᴛ Dᴏᴡɴʟᴏᴀᴅ :</b> <code>{}</code>
<b>🔗 Tᴇʟᴇɢʀᴀᴍ Sʜᴀʀᴇ :</b> <code>{}</code>
<b>⚡ Mᴀɪɴᴛᴀɪɴᴇᴅ Bʏ : @cryvex4</b>\n"""

    STREAM_TEXT_X = """
<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n
<b>📂 Fɪʟᴇ Nᴀᴍᴇ :</b> <b>{}</b>
<b>📦 Fɪʟᴇ Sɪᴢᴇ :</b> <code>{}</code>\n
<b>📥 Dɪʀᴇᴄᴛ Dᴏᴡɴʟᴏᴀᴅ :</b> <code>{}</code>
<b>⚡ Mᴀɪɴᴛᴀɪɴᴇᴅ Bʏ : @cryvex4</b>\n"""

    BAN_TEXT = "__Sᴏʀʀʏ, Yᴏᴜ ᴀʀᴇ Bᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.__\n\n**[Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ](tg://user?id={})**"


class BUTTON(object):
    START_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')
        ]]
    )
    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')
        ]]
    )
    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')
        ]]
    )
