import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Set it in environment variables.")

# ✅ Initialize Flask
server = Flask(__name__)

# ✅ Initialize Telegram bot **(Properly)**
app = Application.builder().token(TOKEN).build()
BOT = Bot(token=TOKEN)

@server.route('/webhook', methods=['POST'])
@server.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming Telegram updates asynchronously."""
    update = request.get_json()
    print("📩 Received update:", update)

    update_obj = Update.de_json(update, app.bot)

    try:
        # ✅ Process the update directly (no initialize call here)
        await app.process_update(update_obj)
        print("✅ Successfully processed update:", update_obj)
    except Exception as e:
        print(f"⚠️ Error processing update: {e}")

    return {"status": "ok"}, 200


# ✅ Command Handlers
async def start(update: Update, context: CallbackContext):
    """Reply when the /start command is sent."""
    print("🚀 /start command received!")

    chat_id = update.message.chat_id
    print(f"🧐 Chat ID: {chat_id}")

    await update.message.reply_text("🎨 Welcome! Your bot is working!")
    print("✅ Reply sent!")

async def generate_prompt(update: Update, context: CallbackContext):
    """Generate an improved prompt based on user input."""
    user_text = update.message.text.lower().strip()

    DESIGN_STYLES = {
        "modern": "A modern product with sleek surfaces, minimal detailing, and a futuristic look.",
        "minimalist": "A minimalist design featuring clean lines, a monochrome color scheme, and a functional aesthetic.",
        "futuristic": "A futuristic concept with smooth, curved surfaces, glowing neon elements, and advanced materials.",
        "brutalist": "A Brutalist design with sharp, angular forms, raw concrete textures, and bold geometric structures.",
        "industrial": "An industrial-style product using exposed metal elements, rugged textures, and a mechanical aesthetic.",
        "organic": "An organic-shaped design with smooth, flowing curves inspired by nature.",
        "art-deco": "An Art-Deco inspired piece with luxurious metallic accents, bold geometric patterns, and vintage elegance.",
    }

    FORM_SHAPES = {
        "round": "A round and smooth shape with soft transitions.",
        "rectangular": "A rectangular, boxy form with precise edges.",
        "cylindrical": "A cylindrical body with a continuous, sleek surface.",
        "geometric": "A highly geometric structure with defined angles and sharp edges.",
        "organic": "An organic, free-flowing shape inspired by nature.",
        "asymmetrical": "An asymmetrical composition with dynamic balance.",
    }

    AESTHETIC_APPROACHES = {
        "bold": "A bold design that stands out with high contrast and powerful forms.",
        "symmetrical": "A perfectly symmetrical design with balanced proportions.",
        "minimal": "A minimalist aesthetic with reduced detailing and maximum simplicity.",
        "futuristic": "A futuristic look with clean lines and tech-inspired features.",
        "rustic": "A rustic aesthetic with natural textures and raw materials.",
    }

    FUNCTIONAL_ELEMENTS = {
        "buttons": "Incorporates intuitive buttons for easy interaction.",
        "touch-sensitive": "Features a modern, touch-sensitive interface.",
        "ergonomic": "Designed with ergonomic grip and usability in mind.",
        "modular": "A modular design allowing interchangeable components.",
    }

    MATERIALS = {
        "wood": "Made from finely polished wood with natural grain details.",
        "metal": "Constructed from brushed aluminum for a premium feel.",
        "glass": "Designed with transparent or frosted glass surfaces.",
        "carbon fiber": "Features lightweight and strong carbon fiber elements.",
    }

    # Generate improved prompt
    improved_prompt = ""
    if user_text in DESIGN_STYLES:
        improved_prompt += f"{DESIGN_STYLES[user_text]} "
    if user_text in FORM_SHAPES:
        improved_prompt += f"{FORM_SHAPES[user_text]} "
    if user_text in AESTHETIC_APPROACHES:
        improved_prompt += f"{AESTHETIC_APPROACHES[user_text]} "
    if user_text in FUNCTIONAL_ELEMENTS:
        improved_prompt += f"{FUNCTIONAL_ELEMENTS[user_text]} "
    if user_text in MATERIALS:
        improved_prompt += f"{MATERIALS[user_text]} "

    # No valid input case
    if not improved_prompt:
        await update.message.reply_text("❌ I didn't recognize any design parameters. Try something like 'brutalist', 'round', or 'ergonomic'.")
        return

    # Create a "Copy It" button
    keyboard = [[InlineKeyboardButton("📋 Copy It", switch_inline_query=improved_prompt)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"✨ **Updated Prompt:**\n_{improved_prompt}_", reply_markup=reply_markup)

# ✅ Fallback handler for unknown commands
async def unknown(update: Update, context: CallbackContext):
    """Fallback handler for unrecognized commands."""
    await update.message.reply_text("❌ Unknown command. Try /start.")

# ✅ Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_prompt))
app.add_handler(MessageHandler(filters.COMMAND, unknown))

async def main():
    """Starts the bot properly."""
    print("🚀 Bot is starting...")
    
    # ✅ Proper Initialization
    await app.initialize()
    await app.start()
    
    print("✅ Bot is running!")

    # ✅ Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_prompt))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # ✅ Run Flask server asynchronously
    port = int(os.environ.get("PORT", 5000))
    await asyncio.to_thread(server.run, host="0.0.0.0", port=port)



# ✅ Run the bot
if __name__ == "__main__":
    asyncio.run(main())  # ✅ Run the bot correctly with async

print("📌 Registered Handlers:")
for handler in app.handlers[0]:
    print(f"  ➡️ {handler}")
