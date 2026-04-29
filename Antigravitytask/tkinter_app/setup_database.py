"""
Database setup script.

Creates the ``library_db`` database, all required tables, and seeds
a default admin account.  Run this once before launching the app.

Usage:
    python setup_database.py
"""

import mysql.connector
from mysql.connector import Error as MySQLError

from app.config import (
    DB_CONFIG,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_ROLE,
    DEFAULT_ADMIN_USERNAME,
)
from app.services.auth import AuthService


def create_database():
    """Create the library_db database if it does not exist."""
    config = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"✅  Database '{DB_CONFIG['database']}' ready.")
        cursor.close()
        connection.close()
    except MySQLError as err:
        print(f"❌  Failed to create database: {err}")
        raise


def create_tables():
    """Create all application tables."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    tables = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('admin', 'librarian') DEFAULT 'librarian',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """,
        # Members table
        """
        CREATE TABLE IF NOT EXISTS members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            membership_date DATE DEFAULT (CURRENT_DATE),
            is_active BOOLEAN DEFAULT TRUE
        ) ENGINE=InnoDB
        """,
        # Books table
        """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(150) NOT NULL,
            isbn VARCHAR(20) UNIQUE,
            genre VARCHAR(50),
            quantity INT DEFAULT 1,
            available INT DEFAULT 1,
            added_date DATE DEFAULT (CURRENT_DATE)
        ) ENGINE=InnoDB
        """,
        # Lendings table
        """
        CREATE TABLE IF NOT EXISTS lendings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            member_id INT NOT NULL,
            lend_date DATE DEFAULT (CURRENT_DATE),
            due_date DATE NOT NULL,
            return_date DATE NULL,
            fine_amount DECIMAL(10,2) DEFAULT 0.00,
            status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """,
    ]

    for sql in tables:
        cursor.execute(sql)
        table_name = sql.split("EXISTS")[1].split("(")[0].strip()
        print(f"  ✅  Table '{table_name}' ready.")

    connection.commit()
    cursor.close()
    connection.close()
    print("✅  All tables created successfully.")


def seed_admin():
    """Create the default admin account if it doesn't exist."""
    from app.models.user import UserModel

    existing = UserModel.get_by_username(DEFAULT_ADMIN_USERNAME)
    if existing:
        print(f"ℹ️  Admin user '{DEFAULT_ADMIN_USERNAME}' already exists.")
        return

    AuthService.register_user(
        DEFAULT_ADMIN_USERNAME,
        DEFAULT_ADMIN_PASSWORD,
        DEFAULT_ADMIN_ROLE,
    )
    print(f"✅  Admin user '{DEFAULT_ADMIN_USERNAME}' created "
          f"(password: {DEFAULT_ADMIN_PASSWORD}).")


def main():
    """Run the full database setup."""
    print("=" * 50)
    print("  Library Management System — Database Setup")
    print("=" * 50)
    print()

    print("1. Creating database...")
    create_database()
    print()

    print("2. Creating tables...")
    create_tables()
    print()

    print("3. Seeding admin user...")
    seed_admin()
    print()

    print("=" * 50)
    print("  Setup complete! You can now run the app:")
    print("  python -m app.main")
    print("=" * 50)


if __name__ == "__main__":
    main()
