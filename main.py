import telebot
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8870024373:AAEsUSqKTFigXORxBLTV5J9_PxxUDS_J6Ko")
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

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
            # Browser configuration ko human-like dikhane ki koshish
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            # Real desktop window size lagana taaki bot na lage
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            
            page = context.new_page()
            
            # STEALTH ACTIVATION: Yeh line automation fingerprint chhupati hai
            stealth_sync(page)
            
            page.goto("https://mega.nz/register", wait_until="networkidle")
            time.sleep(5)
            
            # Form check aur fill up
            page.wait_for_selector("input[name='email']", timeout=15000)
            page.fill("input[name='email']", email)
            time.sleep(1)
            page.fill("input[name='password']", password)
            time.sleep(1)
            page.fill("input[name='password_confirm']", password)
            time.sleep(1)
            
            # Terms checkbox click
            page.click("input[type='checkbox']") 
            time.sleep(1)
            
            # Register button click
            page.click("button[type='submit']")
            time.sleep(5)
            
            browser.close()
            
        bot.send_message(chat_id, f"📩 Registration request submit ho gayi hai!\n\nAb aapke Gmail par confirmation link aaya hoga, wo poora link mujhe yahan bhejiye:")
        bot.register_next_step_handler(message, verify_link)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Stealth Mode bhi block ho gaya: {str(e)}\n\nMega ne Server IP pe pakad liya hai. Iska aakhiri ilaj paid 2Captcha laga kar captcha todna hi hai.")

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
            stealth_sync(page)
            
            page.goto(link, wait_until="networkidle")
            time.sleep(5)
            
            # Agar verification ke baad dubara password confirmation maange
            if page.locator("input[type='password']").is_visible():
                page.fill("input[type='password']", user_data[chat_id]['password'])
                page.click("button[type='submit']")
                time.sleep(5)
                
            browser.close()
            
        bot.send_message(chat_id, f"🎉 Mubarak ho! Account successfully register aur verify ho gaya hai!\n\n📧 Email: {user_data[chat_id]['email']}\n🔒 Password: {user_data[chat_id]['password']}")
        del user_data[chat_id]
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Verification fail: {str(e)}")

print("Stealth Bot ready for Render...")
bot.infinity_polling(skip_pending=True)
