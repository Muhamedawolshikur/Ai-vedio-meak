import telebot
import asyncio
import aiohttp
import time
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- [ 1. RENDER PORT FIX & SERVER ] ---
# Render የግድ የዌብ ሰርቨር መኖሩን ማረጋገጥ ይፈልጋል
app = Flask('')

@app.route('/')
def home():
    return "AI Video Bot is Live and Healthy!"

@app.route('/health')
def health():
    return "OK", 200

def run():
    # Render የሚሰጠውን PORT በራሱ እንዲያገኝ ያደርጋል
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # ዋናው ፕሮግራም ሲቆም አብሮ እንዲቆም
    t.start()

# --- [ 2. CONFIGURATION ] ---
API_TOKEN = '8629718312:AAFWNd287G53CjIvIBZCKv622xNrDaHO6t8'
ADMIN_ID = 8700421304  
CHANNELS = ["@codex_habesha", "@Officialcoders"] 
CHANNEL_LINKS = ["https://t.me/codex_habesha", "https://t.me/Officialcoders"]
ADMIN_USERNAME = "Bilal_Cipher" 

bot = telebot.TeleBot(API_TOKEN)
users = {} 

# --- [ 3. UI DESIGN ELEMENTS ] ---
DIVIDER = "<b>──────────────────────────────</b>"
STAR = "✨"

# --- [ 4. FUNCTIONS ] ---
def check_join(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

def get_main_menu(uid):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_gen = types.InlineKeyboardButton("🎬 CREATE AI VIDEO", callback_data="gen_vid")
    btn_sup = types.InlineKeyboardButton("👨‍💻 CONTACT OWNER", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn_gen, btn_sup)
    return markup

# --- [ 5. HANDLERS ] ---

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {'is_pro': True}

    if not check_join(uid):
        markup = types.InlineKeyboardMarkup()
        for i, link in enumerate(CHANNEL_LINKS):
            markup.add(types.InlineKeyboardButton(f"📡 CHANNEL {i+1}", url=link))
        markup.add(types.InlineKeyboardButton("✅ VERIFY NOW", callback_data="verify"))
        
        welcome_text = (
            f"<b>{STAR} AI VIDEO ENGINE v3.0 {STAR}</b>\n\n"
            "Welcome! To unlock the power of high-quality AI video generation, please follow our official channels.\n\n"
            f"{DIVIDER}\n"
            "👉 <b>Join the channels and hit Verify!</b>"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")
    else:
        status_text = (
            f"<b>{STAR} AI VIDEO ENGINE v3.0 {STAR}</b>\n\n"
            f"Ready to transform your ideas into reality?\n\n"
            f"💠 <b>Account Status:</b> <code>Unlimited ⚡</code>\n"
            f"💠 <b>Service Speed:</b> <code>High Performance</code>\n\n"
            f"{DIVIDER}\n"
            "<b>Click the button below to start! 👇</b>"
        )
        bot.send_message(message.chat.id, status_text, reply_markup=get_main_menu(uid), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    uid = call.from_user.id
    if call.data == "verify":
        if check_join(uid):
            bot.edit_message_text(
                f"<b>{STAR} ACCESS GRANTED {STAR}</b>\n\n"
                "Your account is now verified! You can start creating amazing AI videos immediately.", 
                call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(uid), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "⚠️ Please join all channels first!", show_alert=True)

    elif call.data == "gen_vid":
        sent = bot.send_message(
            call.message.chat.id, 
            "📝 <b>DESCRIBE YOUR VIDEO</b>\n\n"
            "Type a detailed prompt of what you want to see.\n\n"
            "<i>💡 Tip: Describe the movement, lighting, and style for better results.</i>", 
            parse_mode="HTML"
        )
        bot.register_next_step_handler(sent, lambda msg: asyncio.run(process_video_async(msg)))

async def process_video_async(message):
    uid = message.from_user.id
    prompt = message.text
    if not prompt or prompt.startswith('/'): return

    status_msg = bot.send_message(message.chat.id, "✨ Processing your request...", parse_mode="HTML")

    try:
        api_url = f"https://texttovideo-six.vercel.app/generate?prompt={prompt.replace(' ', '%20')}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=600) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("status") == "success" and "url" in result:
                        video_url = result["url"]
                        try: bot.delete_message(message.chat.id, status_msg.message_id)
                        except: pass
                        
                        caption = (
                            f"<b>{STAR} MASTERPIECE READY {STAR}</b>\n"
                            f"{DIVIDER}\n"
                            f"📜 <b>Prompt:</b> <code>{prompt}</code>\n"
                            f"🤖 <b>AI Model:</b> <code>БILДLΞ</code>\n"
                            f"💠 <b>Community:</b> @CODEX_HABESHA\n"
                            f"{DIVIDER}"
                        )
                        bot.send_video(message.chat.id, video_url, caption=caption, reply_markup=get_main_menu(uid), parse_mode="HTML")
                    else:
                        bot.edit_message_text("❌ <b>AI CORE ERROR</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
                else:
                    bot.edit_message_text("❌ <b>SERVER BUSY</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ <b>CONNECTION TIMEOUT</b>", reply_markup=get_main_menu(uid), parse_mode="HTML")

@bot.message_handler(commands=['bc']) 
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/bc ", "")
        if not text or text == "/bc": return
        for uid in list(users.keys()):
            try: bot.send_message(uid, f"📢 <b>ADMIN BROADCAST</b>\n\n{text}", parse_mode="HTML")
            except: pass

# --- [ 6. EXECUTION ] ---
if __name__ == "__main__":
    print("🚀 Bot is starting with Flask Keep-Alive...")
    keep_alive() # Render እንዳይዘጋው ዌብ ሰርቨሩን ያስነሳል
    
    # Render ላይ አስተማማኝው የፖሊንግ ዘዴ
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(5)
        status_text = (
            f"<b>{STAR} AI VIDEO ENGINE v3.0 {STAR}</b>\n\n"
            f"Ready to transform your ideas into reality?\n\n"
            f"💠 <b>Account Status:</b> <code>Unlimited ⚡</code>\n"
            f"💠 <b>Service Speed:</b> <code>High Performance</code>\n\n"
            f"{DIVIDER}\n"
            "<b>Click the button below to start! 👇</b>"
        )
        bot.send_message(message.chat.id, status_text, reply_markup=get_main_menu(uid), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    uid = call.from_user.id
    if call.data == "verify":
        if check_join(uid):
            bot.edit_message_text(
                f"<b>{STAR} ACCESS GRANTED {STAR}</b>\n\n"
                "Your account is now verified! You can start creating amazing AI videos immediately.", 
                call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(uid), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "⚠️ Please join all channels first!", show_alert=True)

    elif call.data == "gen_vid":
        sent = bot.send_message(
            call.message.chat.id, 
            "📝 <b>DESCRIBE YOUR VIDEO</b>\n\n"
            "Type a detailed prompt of what you want to see.\n\n"
            "<i>💡 Tip: Describe the movement, lighting, and style for better results.</i>", 
            parse_mode="HTML"
        )
        bot.register_next_step_handler(sent, lambda msg: asyncio.run(process_video_async(msg)))

async def process_video_async(message):
    uid = message.from_user.id
    prompt = message.text
    if not prompt or prompt.startswith('/'): return

    # ቀላል እና ውብ ሎዲንግ
    status_msg = bot.send_message(
        message.chat.id, 
        "✨", 
        parse_mode="HTML"
    )

    try:
        api_url = f"https://texttovideo-six.vercel.app/generate?prompt={prompt.replace(' ', '%20')}"

        # Timeout ሰዓቱን ለቪዲዮ ስራ እንዲመች አድርገነዋል
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=600) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("status") == "success" and "url" in result:
                        video_url = result["url"]
                        
                        # ሎዲንግ መልዕክቱን ማጥፋት
                        try: bot.delete_message(message.chat.id, status_msg.message_id)
                        except: pass
                        
                        caption = (
                            f"<b>{STAR} MASTERPIECE READY {STAR}</b>\n"
                            f"{DIVIDER}\n"
                            f"📜 <b>Prompt:</b> <code>{prompt}</code>\n"
                            f"🤖 <b>AI Model:</b> <code>БILДLΞ</code>\n"
                            f"💠 <b>Community:</b> @CODEX_HABESHA\n"
                            f"{DIVIDER}"
                        )
                        
                        bot.send_video(message.chat.id, video_url, caption=caption, reply_markup=get_main_menu(uid), parse_mode="HTML")
                    else:
                        bot.edit_message_text("❌ <b>AI CORE ERROR</b>\nThe server could not process this prompt. Try a different one.", message.chat.id, status_msg.message_id, parse_mode="HTML")
                else:
                    bot.edit_message_text("❌ <b>SERVER BUSY</b>\nThe API server is currently overwhelmed. Please try again in 1 minute.", message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        # ስህተት ሲፈጠር ለተጠቃሚው የሚላክ
        bot.send_message(
            message.chat.id, 
            "⚠️ <b>CONNECTION TIMEOUT</b>\nThe generation is taking too long. The server might be down or busy. Please try again with a shorter prompt.", 
            reply_markup=get_main_menu(uid), parse_mode="HTML"
        )

@bot.message_handler(commands=['bc']) 
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/bc ", "")
        if not text or text == "/bc": return
        for uid in list(users.keys()):
            try: bot.send_message(uid, f"📢 <b>ADMIN BROADCAST</b>\n\n{text}", parse_mode="HTML")
            except: pass

if __name__ == "__main__":
    print("🚀 Bot is Online & Beautified!")
    bot.infinity_polling(timeout=90, long_polling_timeout=20)
