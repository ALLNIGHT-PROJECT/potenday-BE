# Potenday Backend - FastAPI

A modern, fast (high-performance) web API built with FastAPI and PostgreSQL.

## 🚀 Features

- **FastAPI** - Modern Python web framework for building APIs
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL** - Production-ready database
- **JWT Authentication** - Secure token-based authentication
- **Docker Support** - Easy deployment with containers
- **Type Hints** - Full type safety with Pydantic
- **Async/Await** - High-performance async operations

## 📁 Project Structure

```
potenday-BE/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core configurations
│   ├── db/            # Database connections
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── utils/         # Utility functions
│   └── main.py        # Application entry point
├── tests/             # Test files
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── .env.example       # Environment variables example
```

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- PostgreSQL
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd potenday-BE
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 🐳 Docker

Run with Docker Compose:
```bash
docker-compose up --build
```

## 📚 API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user

### Tasks
- `GET /api/v1/tasks` - Get all tasks
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Daily Todos
- `GET /api/v1/todos` - Get todos
- `POST /api/v1/todos` - Create new todo
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo
- `POST /api/v1/todos/reorder` - Reorder todos

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

## 📝 License

MIT License