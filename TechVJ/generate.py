# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351


@Client.on_message(filters.private & filters.command("logout"))
async def logout(bot: Client, message: Message):
    user_id = message.from_user.id
    session = await db.get_session(user_id)

    if not session:
        return await message.reply("**You are not logged in.**")

    await db.set_session(user_id, None)
    await message.reply("**Logout Successfully ✅**")


@Client.on_message(filters.private & filters.command("login"))
async def login(bot: Client, message: Message):
    user_id = message.from_user.id

    # Ensure user exists
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    if await db.get_session(user_id):
        return await message.reply(
            "**You are already logged in.\nUse /logout first.**"
        )

    await message.reply(
        "**How To Create Api Id And Api Hash**\n\n"
        "🎥 https://youtu.be/LDtgwpI-N7M"
    )

    api_id_msg = await bot.ask(
        user_id,
        "<b>Send your API ID\n\nSend /skip to use default</b>",
        filters=filters.text
    )

    if api_id_msg.text == "/skip":
        api_id = API_ID
        api_hash = API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            return await api_id_msg.reply(
                "**API ID must be a number. Use /login again.**"
            )

        api_hash_msg = await bot.ask(
            user_id,
            "<b>Now send your API HASH</b>",
            filters=filters.text
        )
        api_hash = api_hash_msg.text

    phone_msg = await bot.ask(
        user_id,
        "<b>Send your phone number with country code</b>\n"
        "<code>+1234567890</code>",
        filters=filters.text
    )

    if phone_msg.text == "/cancel":
        return await phone_msg.reply("**Process cancelled**")

    phone_number = phone_msg.text

    # 🔥 TEMP CLIENT (NO SQLITE FILE)
    user_client = Client(
        name=":memory:",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    )

    try:
        await user_client.connect()
        sent_code = await user_client.send_code(phone_number)

        otp_msg = await bot.ask(
            user_id,
            "Send OTP like: <code>1 2 3 4 5</code>",
            filters=filters.text,
            timeout=600
        )

        if otp_msg.text == "/cancel":
            return await otp_msg.reply("**Process cancelled**")

        otp = otp_msg.text.replace(" ", "")

        try:
            await user_client.sign_in(
                phone_number,
                sent_code.phone_code_hash,
                otp
            )
        except PhoneCodeInvalid:
            return await otp_msg.reply("**Invalid OTP**")
        except PhoneCodeExpired:
            return await otp_msg.reply("**OTP Expired**")
        except SessionPasswordNeeded:
            pass_msg = await bot.ask(
                user_id,
                "**Two-step enabled. Send password**",
                filters=filters.text
            )
            try:
                await user_client.check_password(pass_msg.text)
            except PasswordHashInvalid:
                return await pass_msg.reply("**Wrong password**")

        session_string = await user_client.export_session_string()

        if len(session_string) < SESSION_STRING_SIZE:
            return await message.reply("**Invalid session generated**")

        await db.set_session(user_id, session_string)
        await db.set_api_id(user_id, api_id)
        await db.set_api_hash(user_id, api_hash)

        await message.reply(
            "**Login Successful ✅**\n\n"
            "If you face AUTH errors, /logout and /login again."
        )

    except PhoneNumberInvalid:
        await message.reply("**Invalid phone number**")
    except ApiIdInvalid:
        await message.reply("**Invalid API ID / HASH**")
    except Exception as e:
        await message.reply(f"**ERROR:** `{e}`")
    finally:
        try:
            await user_client.disconnect()
        except:
            pass
