import pyodbc
import pandas as pd
from faker import Faker
import random
import logging
import os
from datetime import datetime, timedelta

# --- Logging setup ---
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/generate_data_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Config ---
SERVER = "de-training-disney.database.windows.net"
DATABASE = "ecommerce_dw"
USERNAME = "de_admin"
PASSWORD = "AbateLazar@9191"
DRIVER = "ODBC Driver 18 for SQL Server"

fake = Faker("en_GB")
random.seed(42)
Faker.seed(42)

TIERS = ["Bronze", "Silver", "Gold"]
CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]

PRODUCTS = [
    ("Wireless Headphones", "Electronics", 79.99),
    ("Running Shoes", "Sports", 54.99),
    ("Coffee Table", "Home & Garden", 129.99),
    ("Python Programming Book", "Books", 29.99),
    ("Yoga Mat", "Sports", 24.99),
    ("Smart Watch", "Electronics", 199.99),
    ("Winter Jacket", "Clothing", 89.99),
    ("Board Game", "Toys", 34.99),
    ("Desk Lamp", "Home & Garden", 44.99),
    ("Bluetooth Speaker", "Electronics", 59.99),
]


def get_connection():
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )
    return pyodbc.connect(conn_str)


def create_tables(conn):
    logger.info("Creating raw source tables...")
    cursor = conn.cursor()

    cursor.execute("""
        IF OBJECT_ID('raw_customers', 'U') IS NOT NULL DROP TABLE raw_customers;
        CREATE TABLE raw_customers (
            customer_id INT PRIMARY KEY,
            first_name NVARCHAR(50),
            last_name NVARCHAR(50),
            email NVARCHAR(100),
            city NVARCHAR(50),
            country NVARCHAR(50),
            tier NVARCHAR(20),
            signup_date DATE,
            is_active BIT
        );
    """)

    cursor.execute("""
        IF OBJECT_ID('raw_products', 'U') IS NOT NULL DROP TABLE raw_products;
        CREATE TABLE raw_products (
            product_id INT PRIMARY KEY,
            product_name NVARCHAR(100),
            category NVARCHAR(50),
            unit_price DECIMAL(10,2),
            is_active BIT
        );
    """)

    cursor.execute("""
        IF OBJECT_ID('raw_orders', 'U') IS NOT NULL DROP TABLE raw_orders;
        CREATE TABLE raw_orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            product_id INT,
            order_date DATE,
            quantity INT,
            unit_price DECIMAL(10,2),
            discount_pct DECIMAL(5,2),
            total_amount DECIMAL(10,2),
            status NVARCHAR(20)
        );
    """)

    conn.commit()
    logger.info("Tables created successfully.")


def generate_customers(n=100):
    logger.info(f"Generating {n} customers...")
    customers = []
    for i in range(1, n + 1):
        signup = fake.date_between(start_date="-3y", end_date="-1m")
        customers.append({
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "city": fake.city(),
            "country": "United Kingdom",
            "tier": random.choice(TIERS),
            "signup_date": signup,
            "is_active": random.choice([1, 1, 1, 0])
        })
    return pd.DataFrame(customers)


def generate_products():
    logger.info("Generating products...")
    products = []
    for i, (name, category, price) in enumerate(PRODUCTS, start=1):
        products.append({
            "product_id": i,
            "product_name": name,
            "category": category,
            "unit_price": price,
            "is_active": 1
        })
    return pd.DataFrame(products)


def generate_orders(n=500):
    logger.info(f"Generating {n} orders...")
    orders = []
    statuses = ["completed", "completed", "completed", "returned", "cancelled"]
    for i in range(1, n + 1):
        customer_id = random.randint(1, 100)
        product_id = random.randint(1, len(PRODUCTS))
        unit_price = PRODUCTS[product_id - 1][2]
        quantity = random.randint(1, 5)
        discount_pct = random.choice([0, 0, 0, 5, 10, 15])
        discount_amount = round(unit_price * quantity * discount_pct / 100, 2)
        total = round(unit_price * quantity - discount_amount, 2)
        orders.append({
            "order_id": i,
            "customer_id": customer_id,
            "product_id": product_id,
            "order_date": fake.date_between(start_date="-1y", end_date="today"),
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_pct": discount_pct,
            "total_amount": total,
            "status": random.choice(statuses)
        })
    return pd.DataFrame(orders)


def load_dataframe(conn, df, table_name):
    logger.info(f"Loading {len(df)} rows into {table_name}...")
    cursor = conn.cursor()
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["?" for _ in df.columns])
    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    cursor.fast_executemany = True
    cursor.executemany(sql, df.values.tolist())
    conn.commit()
    logger.info(f"{table_name} loaded successfully.")


def main():
    logger.info("Starting data generation pipeline...")
    try:
        conn = get_connection()
        logger.info("Connected to Azure SQL.")

        create_tables(conn)

        customers = generate_customers(100)
        products = generate_products()
        orders = generate_orders(500)

        load_dataframe(conn, customers, "raw_customers")
        load_dataframe(conn, products, "raw_products")
        load_dataframe(conn, orders, "raw_orders")

        conn.close()
        logger.info("Data generation complete. 100 customers, 10 products, 500 orders loaded.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()