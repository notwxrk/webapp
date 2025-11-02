from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from models import Database
from telegram import Bot
from telegram.error import TelegramError
import json

app = Flask(__name__)
CORS(app)
db = Database()

# Telegram bot tokeni
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = Bot(BOT_TOKEN) if BOT_TOKEN else None

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user(user_id)
    if user:
        return jsonify({
            'user_id': user[0],
            'username': user[1],
            'balance': float(user[2])
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = db.get_tasks()
    return jsonify([{
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'reward': float(task[3])
    } for task in tasks])

@app.route('/api/submit-task', methods=['POST'])
def submit_task():
    data = request.json
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    proof_text = data.get('proof_text')
    
    # User tasksga qo'shish
    db.add_user_task(user_id, task_id, proof_text)
    
    # Admin ga xabar yuborish
    if bot:
        try:
            message = f"📋 Yangi vazifa topshirildi!\n\n👤 User: {user_id}\n📝 Vazifa ID: {task_id}\n🔍 Proof: {proof_text}"
            bot.send_message(os.environ.get('ADMIN_CHAT_ID'), message)
        except TelegramError as e:
            print(f"Telegram xatosi: {e}")
    
    return jsonify({'status': 'success'})

@app.route('/api/payout', methods=['POST'])
def create_payout():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    usdt_address = data.get('usdt_address')
    
    # Minimal summa tekshirish
    if amount < 1:
        return jsonify({'error': 'Minimal amount $1'}), 400
    
    # Balansni tekshirish
    user = db.get_user(user_id)
    if user[2] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Payout yaratish
    payout_id = db.create_payout(user_id, amount, usdt_address)
    
    # Admin ga xabar yuborish
    if bot:
        try:
            message = f"💸 Yangi payout so'rovi!\n\n👤 User: {user_id}\n💵 Miqdor: ${amount}\n📍 USDT Manzil: {usdt_address}\n📋 Payout ID: {payout_id}"
            bot.send_message(os.environ.get('ADMIN_CHAT_ID'), message)
        except TelegramError as e:
            print(f"Telegram xatosi: {e}")
    
    return jsonify({'status': 'success', 'payout_id': payout_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
