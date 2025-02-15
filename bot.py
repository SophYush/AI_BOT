import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing. Set it in environment variables.")

# ✅ First, initialize Flask BEFORE using it
server = Flask(__name__)  # Define Flask app here

# ✅ Then initialize the Telegram bot
app = Application.builder().token(TOKEN).build()

# Command handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Your bot is working!")

app.add_handler(CommandHandler("start", start))

# ✅ Webhook route: Now Flask is defined before use
@server.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming Telegram updates."""
    update = request.get_json()
    print("Received update:", update)  # Debugging output
    
    update_obj = Update.de_json(update, app.bot)
    await app.update_queue.put(update_obj)  # Corrected async issue
    
    return {"status": "ok"}

# ✅ Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)


# Define command handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎨 Welcome! Send me a **design style, form, aesthetic approach, material, or functional element**, and I'll generate an improved prompt!"
    )

async def generate_prompt(update: Update, context: CallbackContext):
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

    # Initialize improved prompt
    improved_prompt = ""

    # Match user input with categories
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

    # If no match, suggest improvements
    if not improved_prompt:
        await update.message.reply_text(
            "❌ I didn't recognize any design parameters. Try something like 'brutalist', 'round', or 'ergonomic'."
        )
        return

    # Create a "Copy It" button
    keyboard = [[InlineKeyboardButton("📋 Copy It", switch_inline_query=improved_prompt)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"✨ **Updated Prompt:**\n_{improved_prompt}_", reply_markup=reply_markup)

# Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_prompt))


# Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render needs this
    server.run(host="0.0.0.0", port=port)
