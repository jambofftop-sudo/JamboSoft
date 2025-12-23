import telebot
from telebot import types
import time
import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zhake_ultra_pro_max'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- КОНФИГ ---
BOT_TOKEN = "8378070736:AAHrX9RNxzrzvuq-SMrRUUaiJqxUK-YceOA"
ADMIN_ID = 7803278891
CHANNEL_ID = "@zhakebreinrot"

bot = telebot.TeleBot(BOT_TOKEN)
last_sent_times = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_timer', methods=['GET'])
def check_timer():
    user_ip = request.remote_addr
    curr_t = time.time()
    if user_ip in last_sent_times:
        diff = curr_t - last_sent_times[user_ip]
        if diff < 300:
            return jsonify({"status": "wait", "remaining": int(300 - diff)})
    return jsonify({"status": "ok"})

@app.route('/send_anketa', methods=['POST'])
def send_anketa():
    user_ip = request.remote_addr
    curr_t = time.time()
    sid = request.form.get('sid') # ID для уведомления

    if user_ip in last_sent_times and (curr_t - last_sent_times[user_ip] < 300):
        return jsonify({"status": "wait"}), 400

    try:
        profit = request.form.get('profit')
        unit = request.form.get('unit')
        price = request.form.get('price')
        phone = request.form.get('phone')
        photo = request.files.get('photo')

        if not photo:
            return jsonify({"status": "error", "msg": "Фото обязательно!"}), 400

        # Предпросмотр для админа
        caption = f"🐯 **НОВАЯ ЗАЯВКА**\n\n🪐 Прибыль: {profit} {unit}/сек\n💰 Цена: {price} ₸\n📱 Номер: {phone}"
        
        # Сохраняем данные в callback_data (sid нужен для уведомления)
        callback_data = f"pub|{profit}|{unit}|{price}|{phone}|{sid}"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ПРИНЯТЬ ✅", callback_data=callback_data),
                   types.InlineKeyboardButton("ОТКЛОНИТЬ ❌", callback_data="decline"))

        # Отправляем фото админу
        bot.send_photo(ADMIN_ID, photo.read(), caption=caption, parse_mode="Markdown", reply_markup=markup)

        last_sent_times[user_ip] = curr_t
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error"}), 500

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("pub"):
        _, prof, unit, prc, ph, sid = call.data.split("|")
        
        post_text = (
            f"⚡️ **НОВЫЙ ЛОТ НА РЫНКЕ!** ⚡️\n\n"
            f"🪐 Заработок в секунду: {prof} {unit}\n"
            f"💰 Цена брейнрота: {prc} ТЕНГЕ\n"
            f"📲 Ватцап продавца: {ph}\n\n"
            f"🤝 **Гарант — @Zhakebreinrot**\n\n"
            f"🚀 Успей купить лучший брейнрот!"
        )
        
        # Пересылаем в канал ТО ЖЕ ФОТО, что прислал юзер
        photo_id = call.message.photo[-1].file_id
        bot.send_photo(CHANNEL_ID, photo_id, caption=post_text, parse_mode="Markdown")
        
        # Отправляем сигнал на сайт юзеру
        socketio.emit('anketa_accepted', {'msg': 'Администратор принял вашу продажу!', 'link': 'https://t.me/zhakebreinrot'}, room=sid)
        
        bot.answer_callback_query(call.id, "ОПУБЛИКОВАНО ✅")
    else:
        bot.answer_callback_query(call.id, "ОТКЛОНЕНО ❌")
    
    bot.delete_message(ADMIN_ID, call.message.message_id)

def start_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)