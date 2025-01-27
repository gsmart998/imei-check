## IMEI Checker Backend with Telegram Bot Integration

## Overview

This project is a backend system designed to validate and check IMEI devices using the `imeicheck.net` service. The system includes:

1. A Telegram bot for user interaction and management.
    
2. An API for external requests.
    
3. Authorization mechanisms for secured access.
    

### 1. Access Control

- **Telegram Bot Whitelist**: Access is restricted to users listed in a predefined whitelist.
    
- **Role Management**: User roles (`admin`, `user`) allow for granular control over available commands.
    
- **API Authorization**: External API access is secured via token-based authorization.
    

### 2. Telegram Bot Functionalities

- **Commands**:
    
    - `/start`: Starts the bot and provides an introductory message.
        
    - `/check_imei <imei> <service_id>`: Checks the IMEI against the service and returns information.
        
    - `/balance`: Retrieves the account balance from the IMEI-checking service.
        
    - `/add_user <tg_id> <role>`: Adds a new user (admin only).
        
    - `/change_role <tg_id> <new_role>`: Changes the role of an existing user (admin only). Available roles: `[admin, user]`.
        
    - `/change_status <tg_id> <status>`: Changes the status (active/disabled) of an existing user (admin only). Available statuses: `[active, disabled]`.
        
    - `/help`: Lists all available commands.
        


## Installation

### Prerequisites

- Python 3.12 or higher
    
- SQLite (for the database)
    
- Dependencies listed in `requirements.txt`
    

### Steps

1. **Clone the repository**:
    
    ```
    git clone https://github.com/gsmart998/imei-check.git
    cd imei-check
    ```
    
2. **Create and activate a virtual environment**:
    
    ```
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
    ```
    
3. **Install dependencies**:
    
    ```
    pip install -r requirements.txt
    ```
    
    
5. **Configure environment variables**: Create a `.env` file in the project root and configure the following:
    
    ```
    TG_TOKEN=<Your Telegram Bot Token>
    IMEICHECK_NET_TOKEN=<Your API Token>
    DATABASE_URL="sqlite:///../db/sqlite.db"
    ```
    
6. **Run the bot**:
    
    ```
    python src/main.py
    ```
    

---

## Project Structure

```
├── db
│   └── sqlite.db           # Database file
├── logs
│   └── app.log             # Log file
├── README.md
├── requirements.txt        # Dependencies
└── src
    ├── bot.py              # Telegram bot handlers and logic
    ├── database
    │   ├── database.py     # Database initialization
    │   ├── models.py       # ORM models
    ├── imei_services
    │   ├── imeicheck_net.py # IMEI service integration
    ├── logger_config.py    # Logger configuration
    ├── main.py             # Main entry point
```

---

## Dependencies

Dependencies are managed using `requirements.txt`:

```
certifi==2024.12.14
charset-normalizer==3.4.1
greenlet==3.1.1
idna==3.10
pyTelegramBotAPI==4.26.0
python-dotenv==1.0.1
requests==2.32.3
SQLAlchemy==2.0.37
typing_extensions==4.12.2
urllib3==2.3.0
```


---

## Usage

### Telegram Bot

- To interact with the bot, a user must have an entry in the database with the role `admin`.
    
- Only `admin` users can:
    
    - Add new users with specific roles.
        
    - Change user roles and statuses.

- Command `/check_imei` usage:
    - Send the command `/check_imei` to receive a list of available IMEI-checking services along with their prices.

    - Use the command `/check_imei [IMEI] [service_id]`, specifying the IMEI and the desired service, to retrieve detailed information.


## Logging

All significant events, including errors and successful operations, are logged in the `logs/app.log` file.

---

## Future Enhancements

- Add support for additional IMEI-checking services.
    