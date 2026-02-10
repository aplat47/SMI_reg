from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import asyncio

TOKEN = "8385134574:AAFEPPiQD6DnT1eIXUcho98tETB5smNNIBQ"   # ← вставь новый токен от BotFather
USERS_FILE = "users.txt"
DATA_FILE = "registrations.txt"
ADMIN_ID = 268936036  # ← Вставь сюда свой Telegram ID

# Хранилище состояний пользователей
user_state = {}

# ----------------- ФУНКЦИИ -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.message.from_user.first_name

    # сохраняем user_id
    with open(USERS_FILE, "a+", encoding="utf-8") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

    text = (
        f"{first_name}, добро пожаловать в бот SMI 👋\n\n"
        "Он поможет вам зарегистрироваться на вебинар\n"
        "«Инструменты инвестиций в 2026 году» и получить подарок – Инструкцию для новичков "
        "\"Как открыть счет для торгов и правильно выбрать платформу/банк\" 🎁\n\n"
        "Чтобы завершить регистрацию, оставьте ваш номер телефона по кнопке ниже 👇🏻"
    )

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 Отправить имя и телефон", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(text, reply_markup=keyboard)
    user_state[user_id] = "WAIT_CONTACT"


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_state.get(user_id) != "WAIT_CONTACT":
        return

    contact = update.message.contact
    name = contact.first_name
    phone = contact.phone_number

    # Сохраняем в файл
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name} | {phone}\n")

    # Сохраняем user_id ещё раз (на всякий случай)
    with open(USERS_FILE, "a+", encoding="utf-8") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

    # Сообщение-подтверждение
    await update.message.reply_text("Спасибо! Регистрируем вас...")

    # --- Сообщение 2: картинка + текст + кнопка ---
    text = (
        f"{name}, поздравляю! 🎉\n\n"
        "Вы успешно зарегистрированы на вебинар\n"
        "10 февраля в 19:00\n"
        "«Инструменты инвестиций в 2026 году»\n"
        "Фондовые рынки и как на них зарабатывать в России и США\n\n"
        "📍На эфире вас ждёт:\n"
        "— обзор российского и американского инвестиционных рынков\n"
        "— роль и ситуация с рублем в 2026 году\n"
        "— что происходит с процентной ставкой в США\n"
        "— разбор конкретных акций и причин их роста\n"
        "— и приятный бонус, который раскроем уже в эфире 😉\n\n"
        "Переходите в закрытый канал вебинара —\n"
        "там мы будем делиться всеми новостями и именно туда пришлём ссылку на эфир 👇"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎁 ЗАБРАТЬ ПОДАРОК", url="https://t.me/+a163cq-juqRjMzMy")]]
    )

    # Файл картинки должен лежать рядом с bot.py
    with open("webinar.jpg", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=text,
            reply_markup=keyboard
        )

    user_state[user_id] = "DONE"


async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, нажмите кнопку для отправки контакта ☝️")


# ----------------- РАССЫЛКА -----------------
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❗ Использование:\n/sendall текст рассылки")
        return

    text = " ".join(context.args)

    try:
        with open(USERS_FILE, encoding="utf-8") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        await update.message.reply_text("Нет зарегистрированных пользователей")
        return

    sent = 0
    failed = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=text)
            sent += 1
            await asyncio.sleep(0.05)  # защита от лимитов
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ Рассылка завершена\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )


# ----------------- MAIN -----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text))
    app.add_handler(CommandHandler("sendall", send_all))  # команда рассылки

    app.run_polling()


if __name__ == "__main__":
    main()
