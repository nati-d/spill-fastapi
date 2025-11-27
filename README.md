# Spill Backend

A FastAPI backend service for Telegram authentication and nickname management with Supabase integration.

## Features

- 🔐 **Telegram Authentication**: Secure authentication using Telegram Web App init data validation
- 🎯 **Nickname Management**: Generate unique nickname suggestions and reserve nicknames
- 🗄️ **Supabase Integration**: User profiles stored in Supabase database
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation

## Prerequisites

- Python 3.11 or higher
- Supabase account and project
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spill-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:

   **Windows:**
   ```bash
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- **GET** `/`
  - Returns server health status
  - Response: `{"message": "OK"}`

### Authentication
- **POST** `/auth/telegram`
  - Authenticate user with Telegram init data
  - Body: `init_data` (form data)
  - Response: User profile and optional nickname suggestions if user doesn't have a nickname

### Nickname Management
- **GET** `/nickname/suggestions`
  - Get 3 unique nickname suggestions
  - Response: Array of nickname strings

- **POST** `/nickname/reserve`
  - Reserve a nickname for the authenticated user
  - Headers: `x-telegram-init-data` (required)
  - Body: `nickname` (string)
  - Response: `true` if successful, `409 Conflict` if nickname is already taken

## Project Structure

```
spill-backend/
├── core/
│   └── config.py          # Application configuration and settings
├── database/
│   └── supabase.py        # Supabase client initialization
├── features/
│   ├── auth/
│   │   ├── router.py      # Authentication routes
│   │   ├── schemas.py     # Pydantic models for auth
│   │   └── service.py     # Authentication business logic
│   └── nickname/
│       ├── router.py      # Nickname routes
│       └── service.py    # Nickname generation and reservation logic
├── utils/
│   ├── telegram.py        # Telegram init data validation
│   └── words.py           # Word lists for nickname generation
├── words/
│   ├── adjectives.txt    # Adjective word list
│   ├── colors.txt        # Color word list
│   └── nouns.txt         # Noun word list
├── main.py               # FastAPI application entry point
└── .env                  # Environment variables (not in git)
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Supabase**: Backend-as-a-Service for database and authentication
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI
- **python-dotenv**: Environment variable management

## Database Schema

The `profiles` table should have the following structure:
- `telegram_id` (integer, unique, primary key)
- `telegram_username` (string, nullable)
- `telegram_data` (jsonb)
- `nickname` (string, nullable)

## Security

- Telegram init data is validated using HMAC-SHA256
- Auth data expires after 24 hours
- CORS is configured (adjust `allow_origins` in production)
- Environment variables are used for sensitive credentials

## Development

### Running Tests
```bash
# Add your test commands here
```

### Code Style
The project follows PEP 8 Python style guidelines.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

