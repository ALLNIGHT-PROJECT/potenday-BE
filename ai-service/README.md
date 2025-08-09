# AI Task Manager Service

AI-powered task extraction and management service for Potenday project.

## Overview

This is the Python/FastAPI AI service component that provides:
- Multi-agent task extraction from natural language
- Task analysis and prioritization
- Task decomposition into subtasks
- RESTful API for task management

## Architecture

This service works alongside the Spring Boot backend:
- **Spring Boot** (`/potenday-BE`): Main backend API  
- **AI Service** (`/ai-service`): AI task processing microservice

## Features

- **Multi-Agent AI System**
  - Extract Agent: Automatically extract tasks from natural language text
  - Analyze Agent: Analyze task complexity and dependencies
  - Prioritize Agent: Smart task prioritization
  - Decompose Agent: Break down complex tasks into subtasks

- **Task Management**
  - Create, read, update, delete tasks
  - Filter by status, priority, category
  - AI-powered and manual task creation

- **Production Ready**
  - PostgreSQL database (NCloud compatible)
  - RESTful API with FastAPI
  - Comprehensive API documentation
  - Health checks and monitoring

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL (NCloud Cloud DB supported)
- **AI**: LangChain, OpenRouter/OpenAI
- **ORM**: SQLAlchemy

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-task-manager.git
cd ai-task-manager
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Set up NCloud PostgreSQL

1. Create Cloud DB for PostgreSQL in NCloud Console
2. Configure security group to allow your IP
3. Update DATABASE_URL in .env:
```
DATABASE_URL=postgresql://username:password@xxx.pg.naverncp.com:5432/ai_task_manager?sslmode=require
```

### 6. Initialize database
```bash
# Tables are automatically created on first run
python main.py
```

## Usage

### Start the server
```bash
python main.py
```

The server will be available at:
- API: http://localhost:8090
- API Documentation: http://localhost:8090/docs
- ReDoc: http://localhost:8090/redoc

### API Examples

#### Extract tasks from text
```bash
curl -X POST http://localhost:8090/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Need to prepare team meeting tomorrow at 10am and write report",
    "workflow_type": "full"
  }'
```

#### Get all tasks
```bash
curl http://localhost:8090/api/tasks
```

#### Create manual task
```bash
curl -X POST http://localhost:8090/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review code",
    "description": "Review pull request #123",
    "priority": "HIGH",
    "category": "Development"
  }'
```

#### Complete a task
```bash
curl -X PUT http://localhost:8090/api/task/1/complete
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | System info and health check |
| GET | `/health` | Detailed health check |
| POST | `/api/extract` | Extract tasks from text |
| GET | `/api/tasks` | Get task list with filters |
| GET | `/api/task/{id}` | Get specific task |
| POST | `/api/task` | Create manual task |
| PUT | `/api/task/{id}/complete` | Complete task |
| DELETE | `/api/task/{id}` | Delete task |
| POST | `/api/process` | Process task with AI |

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY`: OpenRouter API key for AI features
- `OPENAI_API_KEY`: Alternative OpenAI API key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8090)
- `DEBUG`: Debug mode (default: false)

### Database Configuration

For production with NCloud PostgreSQL:
1. Use SSL connection: `?sslmode=require`
2. Configure connection pooling in `config.py`
3. Set appropriate pool size based on expected load

## Project Structure

```
ai-task-manager/
├── main.py              # Main application file
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── init_db.sql         # Database initialization (optional)
├── docs/               # Documentation
│   ├── api_specification.html
│   └── current_implementation_journey.html
└── models/             # Data models
    └── __init__.py
```

## Development

### Running in debug mode
```bash
# Set in .env
DEBUG=true
python main.py
```

### Testing
```bash
# Use the interactive API documentation
# Visit http://localhost:8090/docs
```

## Deployment

### Docker (Coming Soon)
```bash
docker build -t ai-task-manager .
docker run -p 8090:8090 --env-file .env ai-task-manager
```

### Production Checklist
- [ ] Configure NCloud PostgreSQL with SSL
- [ ] Set up proper API keys
- [ ] Configure security groups
- [ ] Enable monitoring
- [ ] Set up backup strategy
- [ ] Configure rate limiting

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.