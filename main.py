
# A2Z Support Bot - Telegram Bot with Full Flow (Sales/Support)
# Dependencies: pip install python-telegram-bot requests
# Hosting Recommendation: Replit, Render, Fly.io

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import requests

# States
CHOOSING, SALES, SUPPORT, GET_CONTACT = range(4)

user_context = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Sales', 'Support']]
    await update.message.reply_text(
        "Hi! Welcome to A2Z Support. I'm your assistant bot.\nPlease choose an option below:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSING

# MAIN CHOICE
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    user_context[update.effective_user.id] = {'flow': choice.lower()}
    if choice.lower() == "sales":
        reply_keyboard = [['Aircon', 'Smart Home'], ['Smoke Alarm', 'Other']]
        await update.message.reply_text("Great! What product are you interested in?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return SALES
    elif choice.lower() == "support":
        reply_keyboard = [['Aircon', 'Smart Home'], ['Smoke Alarm', 'Other']]
        await update.message.reply_text("Which product do you need help with?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return SUPPORT
    else:
        await update.message.reply_text("Invalid choice.")
        return CHOOSING

# SALES PRODUCT SELECTION
async def handle_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product = update.message.text
    user_context[update.effective_user.id]['product'] = product
    info = {
        'Aircon': "Air Conditioning\n- High-efficiency\n- Fast install\n- 2-year warranty",
        'Smart Home': "Smart Home\n- App control\n- Google/Alexa integration\n- Scalable",
        'Smoke Alarm': "Smoke Alarm\n- Early alerts\n- App notifications\n- Bundles",
        'Other': "Let us know what you need!"
    }
    await update.message.reply_text(f"{info.get(product, 'Product not found')}\n\nPlease enter your full name and phone number:")
    return GET_CONTACT

# SUPPORT PRODUCT SELECTION
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product = update.message.text
    user_context[update.effective_user.id]['product'] = product
    tips = {
        'Smart Home': "Quick Tips:\n- Check WiFi\n- Restart device",
        'Smoke Alarm': "Quick Tips:\n- Check WiFi\n- Test with remote"
    }
    if product in tips:
        await update.message.reply_text(tips[product])
    await update.message.reply_text("Please describe the issue and include your full name and phone number:")
    return GET_CONTACT

# CONTACT COLLECTION
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    flow = user_context[user_id]['flow']
    product = user_context[user_id]['product']
    message = update.message.text

    # Forward to group (replace -100xxxx with your team group ID)
    team_group_id = -1001234567890  # <--- Replace this with your actual group ID
    await context.bot.send_message(
        chat_id=team_group_id,
        text=f"📥 New {flow.capitalize()} Request\nProduct: {product}\nMessage: {message}"
    )

    # Send to Google Sheets via webhook (replace with actual URL)
    webhook_url = "https://your-google-script-url"
    data = {
        'flow': flow,
        'product': product,
        'message': message,
        'username': update.effective_user.username or "NoUsername"
    }
    try:
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass

    await update.message.reply_text("Thanks! Our team will be in touch with you shortly.")
    return ConversationHandler.END

# MAIN APP
def main():
    app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            SALES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sales)],
            SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support)],
            GET_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
