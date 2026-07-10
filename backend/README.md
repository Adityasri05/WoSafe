# WoSafe Backend — Quick Start

## 🛡️ AI-Powered Women's Safety Intelligence Platform

> "AI That Protects Before Danger Begins."

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (recommended)

### Quick Start with Docker

```bash
cd backend

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# API will be available at:
# http://localhost:8000/docs  (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Local Development Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (separate terminal)
celery -A app.jobs.celery_app worker --loglevel=info

# Run tests
pytest tests/ -v
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health

### Architecture

```
backend/
├── app/
│   ├── api/v1/          # REST API routes (15 modules)
│   ├── ai/              # AI Safety Engine
│   ├── core/            # Config, Security, Dependencies, Exceptions
│   ├── database/        # SQLAlchemy Base & Session
│   ├── jobs/            # Celery background tasks
│   ├── middlewares/     # Security headers, logging, rate limiting
│   ├── models/          # 23 PostgreSQL models
│   ├── notifications/   # FCM, Twilio SMS/Voice, Email
│   ├── repositories/    # Data access layer (Repository pattern)
│   ├── schemas/         # Pydantic request/response models
│   ├── security/        # Encryption, validation, audit
│   ├── services/        # Business logic (Service layer)
│   ├── utils/           # Pagination, geocoding, datetime
│   ├── websocket/       # Real-time WebSocket handlers
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── nginx/               # NGINX reverse proxy config
├── tests/               # Pytest test suite
├── docker-compose.yml   # Full-stack Docker setup
├── Dockerfile           # Multi-stage production build
└── pyproject.toml       # Python dependencies
```
