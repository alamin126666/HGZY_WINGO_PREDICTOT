import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import json
import random
from datetime import datetime, timezone
import time
import threading
import requests

TOKEN = "7206852539:AAFjlV9E_FEpBM8vibCJaCRqxJp7XoNlrw4"  # Replace this with your bot token
bot = telebot.TeleBot(TOKEN)

try:
    with open("channels.json", "r") as f:
        data = json.load(f)
except:
    data = {"channels": {}, "signal_on": [], "predictions": {}}
    with open("channels.json", "w") as f:
        json.dump(data, f)

def save_data():
    with open("channels.json", "w") as f:
        json.dump(data, f)

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("SIGNAL ON", "SIGNAL OFF")
    markup.row("ADD CHANNEL", "CHANNEL LIST")
    bot.send_message(message.chat.id, "**💢 𝐇𝐆𝐙𝐘 𝐀𝐔𝐓𝐎 𝐏𝐑𝐄𝐃𝐈𝐂𝐓𝐈𝗢𝗡 💢**\n\n**🚨 আমাদের বটে আপনাকে স্বাগতম আপনি এই বোট এর মাধ্যমে অটোমেটিক আপনার চ্যানেলে সিগনাল নিতে পারবেন।**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ADD CHANNEL")
def ask_channel(message):
    msg = bot.send_message(message.chat.id, "**⛔ ENTER YOUR CHANNEL LINK OR ID ⬇️**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, add_channel)

def add_channel(message):
    if message.text.startswith("-100"):
        link = message.text.strip()
    else:
        link = message.text.replace("https://t.me/", "@")
    data["channels"][link] = True
    save_data()
    bot.send_message(message.chat.id, "**🔴 CHANNEL ADDED SUCCESSFULLY ✅**", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "CHANNEL LIST")
def channel_list(message):
    if data["channels"]:
        msg = "**🔘 ALL CHANNEL LINK ⬇️**\n\n"
        for ch in data["channels"]:
            msg += f"CHANNEL LINK ———> `{ch}`\n"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "**No channel added yet.**", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "SIGNAL ON")
def signal_on(message):
    markup = InlineKeyboardMarkup()
    for ch in data["channels"]:
        markup.add(InlineKeyboardButton(ch, callback_data=f"on|{ch}"))
    bot.send_message(message.chat.id, "**Select channel to SIGNAL ON**", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "SIGNAL OFF")
def signal_off(message):
    markup = InlineKeyboardMarkup()
    for ch in data["channels"]:
        markup.add(InlineKeyboardButton(ch, callback_data=f"off|{ch}"))
    bot.send_message(message.chat.id, "**Select channel to SIGNAL OFF**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, ch = call.data.split("|")
    if action == "on":
        if ch not in data["signal_on"]:
            data["signal_on"].append(ch)
            save_data()
        bot.answer_callback_query(call.id, f"Signal ON for {ch}")
    elif action == "off":
        if ch in data["signal_on"]:
            data["signal_on"].remove(ch)
            save_data()
        bot.answer_callback_query(call.id, f"Signal OFF for {ch}")

def get_period_id():
    now = datetime.now(timezone.utc)
    date = now.strftime("%Y%m%d")
    minutes = now.hour * 60 + now.minute
    period = 10000 + minutes + 1
    return f"{date}{period}"

def generate_signal(period):
    result1 = random.choice(["𝐁𝐈𝐆", "𝐒𝐌𝐀𝐋𝐋"])
    result2 = random.choice(["🟢", "🔴"])
    result3 = random.choice(["𝟷", "𝟸", "𝟹", "𝟺", "𝟻", "𝟼", "𝟽", "𝟾", "𝟿", "𝟶"])
    return result1, result2, result3

def auto_predict():
    last_period = None
    while True:
        current = get_period_id()
        if current != last_period:
            last_period = current
            r1, r2, r3 = generate_signal(current)
            msg = f"""**💢 𝗛𝗚𝗭𝗬 𝗔𝗨𝗧𝗢 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡 💢**

**⏳ 𝙿𝙴𝚁𝙸𝙾𝙳 𝙸𝙳 : {current}**

**🚨 𝚁𝙴𝚂𝚄𝙻𝚃 --> {r1} + {r2} + {r3}**

**⭕ ᗰᑌՏT ᗷᗴ 7-8 ՏTᗴᑭ ᗰᗩIᑎTᗩIᑎ.**"""
            data["predictions"][current] = {"r1": r1, "r2": r2, "r3": r3}
            save_data()
            for ch in data["signal_on"]:
                try:
                    bot.send_message(ch, msg, parse_mode="Markdown")
                except:
                    pass
        time.sleep(1)

def result_checker():
    while True:
        try:
            response = requests.get("https://api.dkwinapi.com/api/webapi/GetNoaverageEmerdList")
            results = response.json()
            for item in results:
                pid = item["GameNo"]
                if pid in data["predictions"]:
                    pred = data["predictions"][pid]
                    actual1 = item.get("Result", "")
                    actual2 = item.get("Color", "")
                    actual3 = item.get("SingleNo", "")

                    pred_match = (
                        pred["r1"] == actual1 and 
                        pred["r2"] == actual2 and 
                        pred["r3"] == actual3
                    )

                    result_msg = f"""**🎯 RESULT for PERIOD {pid}**

**📊 Prediction → {pred['r1']} + {pred['r2']} + {pred['r3']}**
**✅ Actual → {actual1} + {actual2} + {actual3}**

🎯 RESULT → {"✅ WIN ✅" if pred_match else "❌ LOSS ❌"}"""
                    for ch in data["signal_on"]:
                        try:
                            bot.send_message(ch, result_msg, parse_mode="Markdown")
                        except:
                            pass
                    del data["predictions"][pid]
                    save_data()
        except:
            pass
        time.sleep(10)

threading.Thread(target=auto_predict).start()
threading.Thread(target=result_checker).start()
bot.infinity_polling()