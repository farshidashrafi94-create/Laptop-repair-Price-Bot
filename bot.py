from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import json

ADMIN_ID = 88282290  # ← آی‌دی عددی خودت

PRICES_FILE = "prices.json"

def load_prices():
    with open(PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prices(data):
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

PRICES = load_prices()

CATEGORIES = {
    "c1": "لپ‌تاپ",
    "c2": "کامپیوتر رومیزی",
    "c3": "مانیتور",
    "c4": "نرم‌افزار کامپیوتر"
}

ADMIN_STATE = {}

# ===== Menus =====
def main_menu():
    rows = [[InlineKeyboardButton(v, callback_data=k)] for k, v in CATEGORIES.items()]
    rows.append([InlineKeyboardButton("📞 تماس با ما", callback_data="contact")])
    rows.append([InlineKeyboardButton("ℹ️ راهنما", callback_data="help")])
    return InlineKeyboardMarkup(rows)

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ تغییر قیمت", callback_data="admin_edit")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")]
    ])

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 ربات اعلام قیمت خدمات تعمیراتی",
        reply_markup=main_menu()
    )

# ===== Callbacks =====
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PRICES
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # ===== Home =====
    if data == "home":
        await query.edit_message_text("🏠 منوی اصلی", reply_markup=main_menu())
        return

    # ===== Admin panel =====
    if data == "admin":
        if user_id != ADMIN_ID:
            await query.edit_message_text("⛔ دسترسی ندارید")
            return
        await query.edit_message_text("🎛 پنل ادمین", reply_markup=admin_menu())
        return

    if data == "admin_edit":
        keyboard = [
            [InlineKeyboardButton(v, callback_data=f"admin_cat_{k}")]
            for k, v in CATEGORIES.items()
        ]
        await query.edit_message_text("📂 دسته را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("admin_cat_"):
        cat_key = data.replace("admin_cat_", "")
        cat_name = CATEGORIES[cat_key]

        keyboard = [
            [InlineKeyboardButton(v["title"], callback_data=f"admin_srv_{cat_name}_{k}")]
            for k, v in PRICES[cat_name].items()
        ]

        await query.edit_message_text("🛠 سرویس را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("admin_srv_"):
        _, cat_name, srv_id = data.split("_", 2)
        ADMIN_STATE[user_id] = (cat_name, srv_id)
        await query.edit_message_text(
            "✏️ قیمت جدید را ارسال کنید:\nمثال: 1,000,000 – 2,000,000"
        )
        return

    # ===== Categories =====
    if data in CATEGORIES:
        cat_name = CATEGORIES[data]
        keyboard = [
            [InlineKeyboardButton(v["title"], callback_data=f"s_{k}")]
            for k, v in PRICES[cat_name].items()
        ]
        keyboard.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="home")])
        await query.edit_message_text(f"📋 خدمات {cat_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ===== Service price =====
    if data.startswith("s_"):
        sid = data[2:]
        for cat in PRICES.values():
            if sid in cat:
                srv = cat[sid]
                await query.edit_message_text(
                    f"🛠 {srv['title']}\n\n💰 قیمت: {srv['price']} تومان",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")]
                    ])
                )
                return

# ===== Admin text input =====
async def admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_STATE:
        return

    cat_name, srv_id = ADMIN_STATE.pop(user_id)
    PRICES[cat_name][srv_id]["price"] = update.message.text
    save_prices(PRICES)

    await update.message.reply_text("✅ قیمت با موفقیت بروزرسانی شد")

# ===== Run =====
def main():
   import os
ApplicationBuilder().token(os.getenv("8396797817:AAFRU1quWd7GjQZ69oPY7LzGl1GUpaWDEgQ")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", lambda u, c: u.message.reply_text(
        "🎛 پنل ادمین", reply_markup=admin_menu()
    ) if u.message.from_user.id == ADMIN_ID else u.message.reply_text("⛔ دسترسی ندارید")))

    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

