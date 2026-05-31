import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sari_sari_inventory.db")


def get_connection() -> sqlite3.Connection:
    """Open SQLite3 connection. Raises RuntimeError on failure."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to connect to database: {e}") from e


def initialise(conn: sqlite3.Connection) -> None:
    """Create tables and seed default data if not present."""
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS USERS (
                    userID   INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT    NOT NULL UNIQUE,
                    password TEXT    NOT NULL,
                    role     TEXT    NOT NULL DEFAULT 'staff'
                                CHECK(role IN ('admin','staff','viewer'))
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS PRODUCTS (
                    prodID   INTEGER PRIMARY KEY AUTOINCREMENT,
                    prodCode TEXT    NOT NULL UNIQUE,
                    prodName TEXT    NOT NULL,
                    category TEXT    NOT NULL,
                    price    REAL    NOT NULL CHECK(price >= 0),
                    stock    INTEGER NOT NULL CHECK(stock >= 0),
                    addedBy  INTEGER,
                    FOREIGN KEY (addedBy) REFERENCES USERS(userID)
                        ON DELETE SET NULL
                )
            """)

            #Default accounts
            conn.execute("INSERT OR IGNORE INTO USERS (username,password,role) VALUES ('admin','admin123','admin')")
            conn.execute("INSERT OR IGNORE INTO USERS (username,password,role) VALUES ('staff1','staff123','staff')")
            conn.execute("INSERT OR IGNORE INTO USERS (username,password,role) VALUES ('viewer1','view123','viewer')")

            #Pre-populated sample products
            samples = [
                ("P001", "Coca-Cola 1.5L",     "Beverages",    65.00, 30, 1),
                ("P002", "Skyflakes Crackers",  "Snacks",       15.00, 50, 1),
                ("P003", "Century Tuna 155g",   "Canned Goods", 28.00, 40, 1),
                ("P004", "Palmolive Shampoo",   "Personal Care",89.00, 20, 1),
                ("P005", "Datu Puti Vinegar",   "Condiments",   22.00, 35, 1),
                ("P006", "Bear Brand Milk",     "Dairy",        14.50,  4, 1),
                ("P007", "Lucky Me Pancit",     "Snacks",       15.00, 60, 2),
                ("P008", "Ariel Powder 1kg",    "Household",    95.00, 15, 2),
                ("P009", "Sprite 1.5L",         "Beverages",    62.00, 25, 2),
                ("P010", "Eden Cheese 165g",    "Dairy",        75.00,  3, 2),
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO PRODUCTS "
                "(prodCode,prodName,category,price,stock,addedBy) VALUES (?,?,?,?,?,?)",
                samples,
            )
    except sqlite3.Error as e:
        raise RuntimeError(f"Database initialisation failed: {e}") from e
