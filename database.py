import sqlite3
from datetime import datetime

DB_NAME = "database.sqlite3"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel pengguna
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Tabel produk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            file_name TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Tabel pesanan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            telegram_id INTEGER NOT NULL,
            product_id INTEGER,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            paid_at TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()


def add_user(telegram_id, username=None, first_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (telegram_id, username, first_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        username,
        first_name,
        datetime.now().isoformat()
    ))

    # Perbarui data jika user sudah ada
    cursor.execute("""
        UPDATE users
        SET username = ?, first_name = ?
        WHERE telegram_id = ?
    """, (
        username,
        first_name,
        telegram_id
    ))

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))

    user = cursor.fetchone()
    conn.close()

    return user


def add_product(name, description, price, file_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, description, price, file_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        description,
        price,
        file_name,
        datetime.now().isoformat()
    ))

    product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return product_id


def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        ORDER BY id DESC
    """)

    products = cursor.fetchall()
    conn.close()

    return products


def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()
    conn.close()

    return product


def create_order(order_code, telegram_id, product_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
        (order_code, telegram_id, product_id, amount, status, created_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (
        order_code,
        telegram_id,
        product_id,
        amount,
        datetime.now().isoformat()
    ))

    order_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return order_id


def get_order(order_code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM orders
        WHERE order_code = ?
    """, (order_code,))

    order = cursor.fetchone()
    conn.close()

    return order


def get_user_orders(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            orders.*,
            products.name AS product_name
        FROM orders
        LEFT JOIN products
        ON orders.product_id = products.id
        WHERE orders.telegram_id = ?
        ORDER BY orders.id DESC
    """, (telegram_id,))

    orders = cursor.fetchall()
    conn.close()

    return orders


def update_order_status(order_code, status):
    conn = get_connection()
    cursor = conn.cursor()

    if status == "PAID":
        cursor.execute("""
            UPDATE orders
            SET status = ?, paid_at = ?
            WHERE order_code = ?
        """, (
            status,
            datetime.now().isoformat(),
            order_code
        ))
    else:
        cursor.execute("""
            UPDATE orders
            SET status = ?
            WHERE order_code = ?
        """, (
            status,
            order_code
        ))

    conn.commit()
    conn.close()


# Membuat database dan tabel secara otomatis
if __name__ == "__main__":
    init_database()
    print("Database berhasil dibuat.")
