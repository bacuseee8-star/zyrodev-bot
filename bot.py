import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_NAME = "database.sqlite3"


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, username)
        VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()


@dp.message(CommandStart())
async def start_command(message: types.Message):
    user = message.from_user

    add_user(
        user.id,
        user.username
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Katalog Produk",
                    callback_data="catalog"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Pesanan Saya",
                    callback_data="orders"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Bantuan",
                    callback_data="help"
                )
            ]
        ]
    )

    await message.answer(
        f"👋 Halo, {user.first_name}!\n\n"
        "Selamat datang di bot toko digital.\n\n"
        "Silakan pilih menu di bawah:",
        reply_markup=keyboard
    )


@dp.message(Command("menu"))
async def menu_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Katalog Produk",
                    callback_data="catalog"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Pesanan Saya",
                    callback_data="orders"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Bantuan",
                    callback_data="help"
                )
            ]
        ]
    )

    await message.answer(
        "📋 Menu Utama\n\nSilakan pilih:",
        reply_markup=keyboard
    )


@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data == "catalog":
        await callback.message.answer(
            "🛍️ KATALOG PRODUK\n\n"
            "Belum ada produk.\n"
            "Produk akan ditambahkan melalui panel admin."
        )

    elif callback.data == "orders":
        await callback.message.answer(
            "📦 PESANAN SAYA\n\n"
            "Kamu belum memiliki pesanan."
        )

    elif callback.data == "help":
        await callback.message.answer(
            "ℹ️ BANTUAN\n\n"
            "Gunakan /start untuk membuka menu utama.\n"
            "Gunakan /menu untuk melihat menu."
        )

    await callback.answer()


async def main():
    init_database()

    print("🤖 Bot sedang berjalan...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
