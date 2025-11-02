import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from models import Database

# Logging sozlash
logging.basicConfig(level=logging.INFO)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Admin panelga xush kelibsiz!')

async def handle_task_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bu handler userlardan kelgan task submissionlarni qayta ishlaydi
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(':')
    action = data[0]
    task_id = data[1]
    
    if action == 'approve_task':
        # Taskni approve qilish
        db.approve_task(task_id)
        await query.edit_message_text(f"Task #{task_id} approved!")
    elif action == 'reject_task':
        # Taskni reject qilish
        db.reject_task(task_id, "Admin tomonidan rad etildi")
        await query.edit_message_text(f"Task #{task_id} rejected!")

def main():
    app = Application.builder().token(os.environ['BOT_TOKEN']).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_task_submission))
    
    app.run_polling()

if __name__ == '__main__':
    main()
