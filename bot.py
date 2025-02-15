import os  # ✅ Ensure this is the first import
import logging
import queue
import threading
import time
import traceback
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters


# Enable logging
import logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Set it in environment variables.")

# ✅ Initialize Flask before using it
server = Flask(__name__)

# ✅ Initialize Telegram bot
app = Application.builder().token(TOKEN).build()
BOT = Bot(token=TOKEN)  # For manual API calls

# ✅ Replace `asyncio.Queue` with a standard queue
update_queue = queue.Queue()

# ✅ Background thread to process updates
def process_updates():
    """Continuously process updates from the queue."""
    while True:
        try:
            update = update_queue.get(block=True)  # ✅ Use blocking get()
            print("🔄 Processing update:", update)

            if not update.message:
                print("⚠️ Update has no message. Skipping...")
                continue

            # ✅ Print full update object for debugging
            print(f"🧐 Full update object: {update.to_dict()}")

            app.process_update(update)
            print("✅ Successfully processed update:", update)
        except Exception as e:
            print(f"⚠️ Error processing update: {e}")
            print(traceback.format_exc())
            time.sleep(1)

# Start the background processing thread
update_thread = threading.Thread(target=process_updates, daemon=True)
update_thread.start()

# ✅ Webhook route for Telegram
@server.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates."""
    update = request.get_json()
    print("📩 Received update:", update)  # Debugging output

    update_obj = Update.de_json(update, app.bot)

    try:
        update_queue.put(update_obj)  # ✅ Use standard queue put()
        print("✅ Update added to queue:", update_obj)
    except Exception as e:
        print(f"⚠️ Error adding update to queue: {e}")

    return {"status": "ok"}

# ✅ Command handlers
async def start(update: Update, context: CallbackContext):
    """Reply when the /start command is sent."""
    print("🚀 /start command received!")  # Debugging log
    await update.message.reply_text("🎨 Welcome! Send me a **design style, form, aesthetic approach, material, or functional element**, and I'll generate an improved prompt!")

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

# ✅ Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
