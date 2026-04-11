# Vouch - Receipt Analysis Application

AI-powered receipt analysis and search application with support for multiple LLM providers (Ollama, OpenAI, Gemini), built with FastAPI, MongoDB, and Elasticsearch.

## Features

- **Receipt Upload**: Drag-and-drop interface for JPG, PNG, and PDF files (max 5MB)
- **Multi-Provider AI**: Choose between Ollama (local), OpenAI, or Google Gemini for receipt analysis
- **AI Analysis**: Automatic extraction of receipt data using vision models
- **Smart Storage**: MongoDB for document storage with efficient indexing
- **Full-Text Search**: Elasticsearch-powered search across stores, products, UPCs, and transactions
- **Receipt Management**: Upload, search, view, and delete receipts via REST API
- **Warranty Tracking**: Automatic warranty lookup for items $100+
- **Modern UI**: Responsive interface with HTMX for dynamic updates
- **Health Monitoring**: Health check endpoint with proper HTTP status codes (200/503)
- **CORS Support**: Cross-Origin Resource Sharing middleware enabled
- **CI/CD**: GitHub Actions pipeline for linting, testing, and Docker builds
- **Flexible Deployment**: Run locally with Ollama or use cloud APIs (OpenAI/Gemini)

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **Vision AI**: Multi-provider support
  - **Ollama** (default) - Local, private, free
  - **OpenAI** - Cloud-based, GPT-4 Vision
  - **Google Gemini** - Cloud-based, free tier available
- **Database**: MongoDB
- **Search**: Elasticsearch
- **Frontend**: Jinja2 templates + HTMX
- **File Processing**: Pillow, PyPDF, pdf2image

## Quick Start with Docker (Recommended)

The easiest way to run Vouch is using Docker Compose, which includes all dependencies.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

### Build & Deploy

```bash
# Clone the repository
git clone <repository-url>
cd vouch

# Build and start all services
make install

# Or without make:
docker-compose up -d
```

**Note:** First startup takes 5-15 minutes to download the Ollama model (~4.7GB).

### Monitor & Manage

```bash
make status        # Show status of all services
make logs          # View logs from all services
make health        # Check health of all services
make restart       # Restart all services
make down          # Stop all services
make clean         # Remove containers and volumes
```

### Access Application

Once all services are healthy:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- MongoDB 7.0+
- Elasticsearch 8.12+
- An LLM provider (Ollama, OpenAI, or Gemini)
- poppler-utils (for PDF processing)

### Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (production + development)
uv pip install -r requirements-dev.txt

# Or install production dependencies only
uv pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (MongoDB URL, LLM provider, API keys, etc.)
```

### Start Development Server

```bash
# Using make
make dev-server

# Or directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Build, Test & Deploy Commands

All commands use `make` for convenience. Run `make help` to see all available commands.

### Development

| Command | Description |
|---------|-------------|
| `make install-dev` | Install all dependencies (prod + dev) using uv |
| `make dev-server` | Start development server with hot-reload |
| `make format` | Auto-format code with isort and black |
| `make lint` | Run all linters (isort, black, flake8) |
| `make security-scan` | Run bandit security scanner |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run unit tests (excludes integration/slow tests) |
| `make test-all` | Run all tests including integration tests |
| `pytest -m unit` | Run only unit-marked tests |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Re-run last failed tests |
| `pytest --durations=10` | Show 10 slowest tests |

### Docker / Deploy

| Command | Description |
|---------|-------------|
| `make build` | Build Docker images |
| `make up` | Start all services in background |
| `make down` | Stop all services |
| `make install` | Build and start (first-time setup) |
| `make logs` | Tail logs from all services |
| `make status` | Show container status |
| `make health` | Check service health endpoints |
| `make restart` | Restart all services |
| `make clean` | Remove containers and volumes |
| `make backup-mongodb` | Backup MongoDB data |
| `make restore-mongodb FILE=<path>` | Restore MongoDB from backup |

---

## LLM Providers

Vouch supports three LLM providers for receipt analysis:

| Provider | Cost | Privacy | Setup | API Key | Best For |
|----------|------|---------|-------|---------|----------|
| **Ollama** | Free | High (local) | Medium | No | Privacy, self-hosting, development |
| **OpenAI** | ~$0.01-0.03/receipt | Low (cloud) | Easy | Yes | Production, accuracy, speed |
| **Gemini** | Free tier + paid | Low (cloud) | Easy | Yes | Cost optimization, free tier |

### Quick Provider Setup

**Ollama (Default):**
```bash
ollama pull llava
ollama serve
```

**OpenAI:** Add to `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

**Gemini:** Add to `.env`:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```

For detailed setup instructions, see [PROVIDER_SETUP_GUIDE.md](PROVIDER_SETUP_GUIDE.md).

---

## API Endpoints

### Upload Receipt
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/receipt.jpg"
```

### Search Receipts
```bash
curl "http://localhost:8000/api/search?q=Home+Depot&min_price=50"
```

### Get Single Receipt
```bash
curl "http://localhost:8000/api/receipts/{receipt_id}"
```

### List All Receipts
```bash
curl "http://localhost:8000/api/receipts?skip=0&limit=20"
```

### Delete Receipt
```bash
curl -X DELETE "http://localhost:8000/api/receipts/{receipt_id}"
```

### Health Check
```bash
curl "http://localhost:8000/health"
# Returns 200 when healthy, 503 when degraded
```

---

## Project Structure

```
vouch/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration with multi-provider support
│   ├── models.py                    # Pydantic models
│   ├── services/
│   │   ├── base_llm_service.py     # Abstract base class for LLM providers
│   │   ├── llm_factory.py          # Factory pattern for provider selection
│   │   ├── image_utils.py          # Shared image processing utilities
│   │   ├── ollama_service.py       # Ollama provider implementation
│   │   ├── openai_service.py       # OpenAI provider implementation
│   │   ├── gemini_service.py       # Google Gemini provider implementation
│   │   ├── mongodb_service.py      # MongoDB operations
│   │   └── elasticsearch_service.py # Search functionality
│   ├── routers/
│   │   ├── upload.py               # File upload endpoints
│   │   └── search.py               # Search and receipt management endpoints
│   ├── static/                     # CSS and JS assets
│   └── templates/                  # Jinja2 HTML templates
├── tests/                          # Test suite
│   ├── conftest.py                 # Shared fixtures
│   ├── test_config.py              # Configuration tests
│   ├── test_models.py              # Pydantic model tests
│   ├── routers/                    # Router integration tests
│   └── services/                   # Service unit tests
├── .github/workflows/ci.yml       # GitHub Actions CI pipeline
├── pyproject.toml                  # Project config, dependencies, tool settings
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies (includes prod)
├── Dockerfile                      # Multi-stage Docker build (uses uv)
├── docker-compose.yml              # Full stack orchestration
├── Makefile                        # Build, test, and deploy commands
├── prompt.txt                      # LLM prompt template
└── receipt-breakdown-schema.json   # JSON schema for receipt validation
```

## Testing

The test suite uses pytest with async support and covers:

- **Configuration** (`tests/test_config.py`) - Settings defaults and overrides
- **Models** (`tests/test_models.py`) - Pydantic model validation
- **Services** (`tests/services/`) - LLM providers, MongoDB, Elasticsearch, image utils, factory
- **Routers** (`tests/routers/`) - Upload and search endpoint integration tests

Test markers: `unit`, `integration`, `slow`, `requires_services`, `llm`

```bash
# Quick: run unit tests only
make test

# Full: run all tests
make test-all

# Coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Documentation

- **[PROVIDER_SETUP_GUIDE.md](PROVIDER_SETUP_GUIDE.md)** - Detailed LLM provider setup
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration guide for existing users
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[DOCKER.md](DOCKER.md)** - Detailed Docker documentation
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing patterns and guide

## License

MIT License
