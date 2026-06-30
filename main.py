import telebot
from playwright.sync_api import sync_playwright
import time
import os

# Telegram Bot Token (Render par environment variable se lena safe hota hai)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8870024373:AAEsUSqKTFigXORxBLTV5J9_PxxUDS_J6Ko")
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Mega.nz Auto-Register Bot active hai!\nNaya account banane ke liye /create_account type karein.")

@bot.message_handler(commands=['create_account'])
def ask_email(message):
    msg = bot.reply_to(message, "📧 Step 1: Gmail ID bhejiye:")
    bot.register_next_step_handler(msg, get_email)

def get_email(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'email': message.text.strip()}
    msg = bot.reply_to(message, "🔒 Step 2: Password bhejiye:")
    bot.register_next_step_handler(msg, get_password)

def get_password(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "❌ Error! Dubara shuru karein.")
        return
        
    user_data[chat_id]['password'] = message.text.strip()
    email = user_data[chat_id]['email']
    password = user_data[chat_id]['password']
    
    bot.send_message(chat_id, "🔄 Render server par Chrome browser open ho raha hai... Mega par registration chal rahi hai, 15-20 seconds rukein...")
    
    try:
        with sync_playwright() as p:
            # Linux server par sandbox disable karna zaroori hai
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page()
            
            page.goto("https://mega.nz/register", wait_until="networkidle")
            time.sleep(3)
            
            # Form fill up
            page.fill("input[name='email']", email)
            page.fill("input[name='password']", password)
            page.fill("input[name='password_confirm']", password)
            
            # Terms checkbox click
            page.click("input[type='checkbox']") 
            
            # Submit/Register button click
            page.click("button[type='submit']")
            time.sleep(5)
            browser.close()
            
        bot.send_message(chat_id, f"📩 Maine '{email}' se register kar diya hai!\n\nAb aapke Gmail par confirmation link aaya hoga, wo poora link mujhe yahan bhejiye:")
        bot.register_next_step_handler(message, verify_link)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Server Error: {str(e)}\nShayad Mega ne Captcha blocking laga di.")

def verify_link(message):
    chat_id = message.chat.id
    link = message.text.strip()
    
    if "mega.nz" not in link:
        bot.reply_to(message, "❌ Sahi Mega link bhejiye.")
        return

    bot.send_message(chat_id, "⚡ Link ko server browser mein verify kiya ja raha hai...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page()
            page.goto(link, wait_until="networkidle")
            time.sleep(5)
            
            # Agar password confirmation maange
            if page.locator("input[type='password']").is_visible():
                page.fill("input[type='password']", user_data[chat_id]['password'])
                page.click("button[type='submit']")
                time.sleep(5)
                
            browser.close()
            
        bot.send_message(chat_id, f"🎉 Mubarak ho! Account successfully register aur verify ho gaya hai!\n\n📧 Email: {user_data[chat_id]['email']}\n🔒 Password: {user_data[chat_id]['password']}")
        del user_data[chat_id]
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Verification fail: {str(e)}")

print("Bot is ready for Render...")
bot.infinity_polling(skip_pending=True)
