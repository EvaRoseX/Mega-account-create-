import telebot
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth  # <--- Clean and correct import
import time
import os
import threading
import http.server
import socketserver

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8870024373:AAEsUSqKTFigXORxBLTV5J9_PxxUDS_J6Ko")
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Aapki Real Telegram ID
OWNER_ID = 8391386178

user_data = {}

# 📢 STARTUP NOTIFICATION
try:
    bot.send_message(OWNER_ID, "🚀 **Bot successfully restart ho gaya he aur active he!**", parse_mode="Markdown")
except Exception as e:
    print(f"Owner ko message nahi bhej paya: {e}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Mega.nz Stealth Auto-Register Bot Active hai!\nAccount banane ke liye /create_account type karein.")


@bot.message_handler(commands=['create_account'])
def ask_email(message):
    msg = bot.reply_to(message, "📧 Step 1: Naye account ki Gmail ID bhejiye:")
    bot.register_next_step_handler(msg, get_email)


def get_email(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'email': message.text.strip()}
    msg = bot.reply_to(message, "🔒 Step 2: Mega account ka naya Password bhejiye:")
    bot.register_next_step_handler(msg, get_password)


def get_password(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "❌ Error! Dubara shuru karein.")
        return
        
    user_data[chat_id]['password'] = message.text.strip()
    email = user_data[chat_id]['email']
    password = user_data[chat_id]['password']
    
    bot.send_message(chat_id, "🔄 Stealth Mode active... Server par registration bypass try ho raha hai, 20-30 seconds rukein...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            
            page = context.new_page()
            
            # 🛠️ 100% VERIFIED STEALTH METHOD CALL
            stealth(page)
            
            page.goto("https://mega.nz/register", wait_until="networkidle")
            time.sleep(5)
            
            page.wait_for_selector("input[name='email']", timeout=15000)
            page.fill("input[name='email']", email)
            time.sleep(1)
            page.fill("input[name='password']", password)
            time.sleep(1)
            page.fill("input[name='password_confirm']", password)
            time.sleep(1)
            
            page.click("input[type='checkbox']") 
            time.sleep(1)
            
            page.click("button[type='submit']")
            time.sleep(5)
            
            browser.close()
            
        bot.send_message(chat_id, f"📩 Registration request submit ho gayi hai!\n\nAb aapke Gmail par confirmation link aaya hoga, wo poora link mujhe yahan bhejiye:")
        bot.register_next_step_handler(message, verify_link)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Engine Error: {str(e)}")


def verify_link(message):
    chat_id = message.chat.id
    link = message.text.strip()
    
    if "mega.nz" not in link:
        bot.reply_to(message, "❌ Sahi Mega verification link bhejiye.")
        return

    bot.send_message(chat_id, "⚡ Link ko stealth browser mein verify kiya ja raha hai...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            page = context.new_page()
            
            # 🛠️ VERIFIED HERE TOO
            stealth(page)
            
            page.goto(link, wait_until="networkidle")
            time.sleep(5)
            
            if page.locator("input[type='password']").is_visible():
                page.fill("input[type='password']", user_data[chat_id]['password'])
                page.click("button[type='submit']")
                time.sleep(5)
                
            browser.close()
            
        bot.send_message(chat_id, f"🎉 Mubarak ho! Account successfully register aur verify ho gaya hai!\n\n📧 Email: {user_data[chat_id]['email']}\n🔒 Password: {user_data[chat_id]['password']}")
        del user_data[chat_id]
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Verification fail: {str(e)}")


# 🌐 DUMMY SERVER FUNCTION
def run_dummy_server():
    PORT = int(os.getenv("PORT", 8000))
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dummy server active on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

print("Stealth Bot ready for Render Free Web Service...")
bot.infinity_polling(skip_pending=True)
