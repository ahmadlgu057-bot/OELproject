# 📚 Library Management System

A comprehensive **Library Management System** built with **Python**, **Tkinter**, and **MySQL**. Features a modern dark-themed GUI with full CRUD operations for managing books, members, lending, returns, fines, and inventory reports.

## ✨ Features

| Panel | Description |
|-------|-------------|
| **Login / Admin Panel** | Secure authentication with bcrypt password hashing |
| **Book Management** | Add, edit, delete, and search books in the catalogue |
| **Member Registration** | Register, update, and deactivate library members |
| **Book Lending** | Lend books to members with automatic due-date calculation |
| **Book Returns** | Process returns with automatic overdue fine calculation |
| **Inventory Reports** | View summary metrics, popular books, genre distribution |
| **Fine Management** | Track outstanding fines by member or library-wide |

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI:** Tkinter (ttk themed widgets)
- **Database:** MySQL 8.0+
- **Password Hashing:** bcrypt
- **Testing:** unittest with mocks

## 📁 Project Structure

```
tkinter_app/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py             # Configuration settings
│   ├── views/                # Tkinter GUI panels
│   │   ├── login.py          # Login window
│   │   ├── dashboard.py      # Dashboard with sidebar navigation
│   │   ├── books.py          # Book CRUD interface
│   │   ├── members.py        # Member management
│   │   ├── lending.py        # Book lending
│   │   ├── returns.py        # Book returns
│   │   ├── reports.py        # Inventory reports
│   │   └── fines.py          # Fine calculation
│   ├── models/               # Data access layer (CRUD)
│   │   ├── user.py           # User model
│   │   ├── book.py           # Book model
│   │   ├── member.py         # Member model
│   │   └── lending.py        # Lending model
│   ├── services/             # Business logic layer
│   │   ├── auth.py           # Authentication service
│   │   ├── book_service.py   # Book management logic
│   │   ├── member_service.py # Member management logic
│   │   ├── lending_service.py# Lending/return logic
│   │   ├── fine_service.py   # Fine calculations
│   │   └── report_service.py # Report generation
│   └── utils/                # Shared utilities
│       ├── database.py       # MySQL connection manager
│       ├── style.py          # Dark theme & widget factories
│       └── validators.py     # Input validation helpers
├── tests/                    # Unit tests
│   ├── test_services/
│   └── test_models/
├── setup_database.py         # One-time DB setup script
└── requirements.txt
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher (running on localhost)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ghazanfarali00/Antigravitytask.git
   cd Antigravitytask/tkinter_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database:**
   ```bash
   python setup_database.py
   ```
   This creates the `library_db` database, tables, and a default admin account.

4. **Run the application:**
   ```bash
   python -m app.main
   ```

### Default Login

- **Username:** `ghazanfar`
- **Password:** `admin123`

## 🧪 Running Tests

```bash
cd tkinter_app
python -m pytest tests/ -v
```

Or with unittest:
```bash
python -m unittest discover -s tests -v
```

## 📋 CRUD Operations

All four CRUD operations are implemented across the system:

- **Create:** Add books, register members, create lending records
- **Read:** Search/view books, members, lendings, fines, reports
- **Update:** Edit book details, update member info, mark returns
- **Delete:** Remove books (with lending checks), deactivate members

## 🎨 Design

The application uses a modern dark theme with:
- Dark navy colour palette
- Accent colours for interactive elements
- Consistent styling across all panels
- Responsive layouts

## 👤 Author

**Ghazanfar Ali** — [github.com/ghazanfarali00](https://github.com/ghazanfarali00)
