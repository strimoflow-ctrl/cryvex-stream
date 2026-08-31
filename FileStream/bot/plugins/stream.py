
import base64
import aiohttp
from FileStream.bot import FileStream, multi_clients
from FileStream.utils.bot_utils import is_user_banned, is_user_exist, is_user_joined, gen_link, is_channel_banned, is_channel_exist, is_user_authorized
from FileStream.utils.database import Database
from FileStream.utils.file_properties import get_file_ids, get_file_info
from FileStream.config import Telegram
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums.parse_mode import ParseMode
from FileStream.utils.groq_parser import parse_lecture_info
from FileStream.utils.firebase_db import push_pending_upload
from FileStream.config import Server

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

# 5 User ImgBB API Keys with Automatic Failover Rotation
IMGBB_API_KEYS = [
    "afc77b68f6c5ae56c42a5b225ef54635",
    "5b7d3b1d031d9d2c7bfc29b59e07987f",
    "d096ed6d78c97436376467bc7ac19f6c",
    "209f45ba726aa6080111cac04ddd61f8",
    "39469af0165ceced8495586e27f55db6"
]

async def upload_thumb_with_key_rotation(bot: Client, message: Message) -> str:
    """
    Downloads video thumbnail from Telegram and uploads to ImgBB.
    Tries each of the 5 API keys sequentially. If one key hits its limit or fails,
    it automatically switches to the next working key!
    """
    try:
        media = getattr(message, 'video', None) or getattr(message, 'document', None) or getattr(message, 'photo', None)
        if not media:
            return ""

        thumbs = getattr(media, 'thumbs', None)
        if not thumbs or not isinstance(thumbs, list):
            return ""

        thumb_file_id = thumbs[-1].file_id
        if not thumb_file_id:
            return ""

        thumb_bytes = await bot.download_media(thumb_file_id, in_memory=True)
        if not thumb_bytes:
            return ""

        b64_data = base64.b64encode(bytes(thumb_bytes.getbuffer())).decode('utf-8')

        async with aiohttp.ClientSession() as session:
            for idx, api_key in enumerate(IMGBB_API_KEYS, 1):
                try:
                    data = aiohttp.FormData()
                    data.add_field('key', api_key)
                    data.add_field('image', b64_data)
                    async with session.post('https://api.imgbb.com/1/upload', data=data, timeout=10) as resp:
                        res_json = await resp.json()
                        if res_json.get('success') and 'data' in res_json and 'url' in res_json['data']:
                            print(f"[ImgBB Success] Uploaded thumbnail using Key #{idx} ({api_key[:8]}...) -> {res_json['data']['url']}")
                            return res_json['data']['url']
                        else:
                            print(f"[ImgBB Key #{idx} Failed] Trying next key... Response: {res_json}")
                except Exception as key_err:
                    print(f"[ImgBB Key #{idx} Error] {key_err}. Trying next key...")
    except Exception as e:
        print(f"Error uploading thumbnail with key rotation: {e}")
    return ""

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
        file_info_obj = get_file_info(message)
        inserted_id = await db.add_file(file_info_obj)
        await get_file_ids(False, inserted_id, multi_clients, message)
        reply_markup, stream_text = await gen_link(_id=inserted_id)

        # Extract raw caption sent by user
        raw_caption = message.caption or message.text or ""
        raw_text = raw_caption or file_info_obj.get('file_name', 'Untitled')
        parsed = await parse_lecture_info(raw_text)
        
        # Upload video thumbnail to ImgBB using 5-key automatic rotation engine
        thumb_url = await upload_thumb_with_key_rotation(bot, message)

        # Build stream link & push to Firebase inbox
        stream_link = f"{Server.URL}dl/{inserted_id}"
        file_name = file_info_obj.get('file_name', 'File')
        file_size = str(file_info_obj.get('file_size', 0))

        pushed = await push_pending_upload(
            file_id=str(inserted_id),
            title=parsed['title'],
            lecture_no=parsed['lecture_no'],
            stream_link=stream_link,
            file_name=file_name,
            file_size=file_size,
            raw_caption=raw_caption,
            thumb_url=thumb_url
        )

        if pushed:
            stream_text += f"\n\n<b>📥 Sent to Admin Inbox!</b>\n<b>Title:</b> {parsed['title']}\n<b>Lec #:</b> {parsed['lecture_no'] if parsed['lecture_no'] != 999 else 'Auto'}"

        await message.reply_text(
            text=stream_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await bot.send_message(chat_id=Telegram.ULOG_CHANNEL,
                               text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s ғʀᴏᴍ [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n**ᴜsᴇʀ ɪᴅ :** `{str(message.from_user.id)}`",
                               disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"Error in private_receive_handler: {e}")
        if Telegram.ULOG_CHANNEL:
            try:
                await bot.send_message(chat_id=Telegram.ULOG_CHANNEL, text=f"**#ErrorInStream:** `{e}`", disable_web_page_preview=True)
            except Exception:
                pass



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

