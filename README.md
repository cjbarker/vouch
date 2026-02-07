# Vouch - Receipt Analysis Application

AI-powered receipt analysis and search application with support for multiple LLM providers (Ollama, OpenAI, Gemini), built with FastAPI, MongoDB, and Elasticsearch.

## Features

- **Receipt Upload**: Drag-and-drop interface for JPG, PNG, and PDF files (max 5MB)
- **Multi-Provider AI**: Choose between Ollama (local), OpenAI, or Google Gemini for receipt analysis
- **AI Analysis**: Automatic extraction of receipt data using vision models
- **Smart Storage**: MongoDB for document storage with efficient indexing
- **Full-Text Search**: Elasticsearch-powered search across stores, products, UPCs, and transactions
- **Warranty Tracking**: Automatic warranty lookup for items $100+
- **Modern UI**: Responsive interface with HTMX for dynamic updates
- **Flexible Deployment**: Run locally with Ollama or use cloud APIs (OpenAI/Gemini)

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Vision AI**: Multi-provider support
  - **Ollama** (default) - Local, private, free
  - **OpenAI** - Cloud-based, GPT-4 Vision
  - **Google Gemini** - Cloud-based, free tier available
- **Database**: MongoDB
- **Search**: Elasticsearch
- **Frontend**: Jinja2 templates + HTMX
- **File Processing**: Pillow, PyPDF2, pdf2image

## LLM Providers

Vouch supports three LLM providers for receipt analysis. Choose based on your needs:

### Provider Comparison

| Provider | Cost | Privacy | Setup | API Key | Best For |
|----------|------|---------|-------|---------|----------|
| **Ollama** | Free | High (local) | Medium | No | Privacy, self-hosting, development |
| **OpenAI** | ~$0.01-0.03/receipt | Low (cloud) | Easy | Yes | Production, accuracy, speed |
| **Gemini** | Free tier + paid | Low (cloud) | Easy | Yes | Cost optimization, free tier |

### Quick Provider Setup

**Using Ollama (Default - No API Key Needed):**
```bash
# Install Ollama
brew install ollama  # macOS

# Pull vision model
ollama pull llama3.2-vision

# Start Ollama
ollama serve
```

**Using OpenAI:**
```bash
# Add to .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```
Get your API key at: https://platform.openai.com/api-keys

**Using Google Gemini:**
```bash
# Add to .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```
Get your API key at: https://makersuite.google.com/app/apikey

For detailed setup instructions, see [PROVIDER_SETUP_GUIDE.md](PROVIDER_SETUP_GUIDE.md)

## Quick Start with Docker (Recommended)

The easiest way to run Vouch is using Docker Compose, which includes all dependencies.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd vouch

# Build and start all services
make install

# Or without make:
docker-compose up -d
```

**Note:**
- First startup takes 5-15 minutes to download the Ollama model (~4.7GB)
- Docker setup uses Ollama by default. To use OpenAI or Gemini, add environment variables to docker-compose.yml

### Monitor Progress

```bash
# Check status
make status

# View logs
make logs

# Check health
make health
```

### Access Application

Once all services are healthy:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Available Commands

```bash
make help          # Show all available commands
make up            # Start services
make down          # Stop services
make logs          # View logs
make restart       # Restart services
make clean         # Remove containers and volumes
```

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

---

## Manual Installation (Alternative)

If you prefer to run without Docker, follow these steps to install and run locally.

### Prerequisites

Before running the application, ensure you have the following installed:

#### 1. Python 3.11 or higher

```bash
python --version
```

**Note:** Python 3.11-3.14+ are supported. If you encounter dependency issues with Python 3.14+, create a fresh virtual environment:

```bash
# Remove old venv if it exists
rm -rf venv .venv

# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. MongoDB

- Download: https://www.mongodb.com/try/download/community
- Or install via package manager:
  ```bash
  # macOS
  brew tap mongodb/brew
  brew update
  brew install mongodb-community

  # Ubuntu
  sudo apt-get install mongodb
  ```

#### 3. Elasticsearch

- Download: https://www.elastic.co/downloads/elasticsearch
- Or install via package manager:
  ```bash
  # macOS
  brew install elasticsearch

  # Ubuntu
  wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
  sudo apt-get install elasticsearch
  ```

#### 4. LLM Provider (Choose One)

**Option A: Ollama (Default - Local & Free)**
- Download: https://ollama.ai/download
- Install the llama3.2-vision model:
  ```bash
  ollama pull llama3.2-vision
  ```

**Option B: OpenAI (Cloud-Based)**
- Get API key: https://platform.openai.com/api-keys
- Add to `.env`: `LLM_PROVIDER=openai` and `OPENAI_API_KEY=sk-...`

**Option C: Google Gemini (Cloud-Based)**
- Get API key: https://makersuite.google.com/app/apikey
- Add to `.env`: `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...`

#### 5. poppler-utils (for PDF processing)

```bash
# macOS
brew install poppler

# Ubuntu
sudo apt-get install poppler-utils
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vouch
   ```

2. **Create a fresh virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate it
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Verify Python version
   python --version
   ```

3. **Upgrade pip and install dependencies**
   ```bash
   # Upgrade pip to latest version
   pip install --upgrade pip

   # Install application dependencies
   pip install -r requirements.txt
   ```

   **Troubleshooting Installation:**
   - If you see errors about `pkgutil.find_loader`, you need a fresh venv (see step 2)
   - If packages fail to install, ensure you're using Python 3.11+
   - For Python 3.14+, the latest package versions should work

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file with your settings:
   ```env
   # Database & Search
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB_NAME=vouch
   ELASTICSEARCH_URL=http://localhost:9200

   # LLM Provider Selection (ollama, openai, or gemini)
   LLM_PROVIDER=ollama

   # Ollama Configuration (default)
   OLLAMA_API_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2-vision

   # OpenAI Configuration (optional)
   # OPENAI_API_KEY=sk-your-key-here
   # OPENAI_MODEL=gpt-4-vision-preview

   # Gemini Configuration (optional)
   # GEMINI_API_KEY=your-key-here
   # GEMINI_MODEL=gemini-1.5-pro-vision

   # File Upload
   MAX_UPLOAD_SIZE=5242880
   UPLOAD_DIR=./uploads
   ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
   ```

### Running the Application Locally

### 1. Start MongoDB

```bash
# macOS/Linux
mongod --dbpath /path/to/your/data/directory

# Or if installed via brew (macOS)
brew services start mongodb-community

# Ubuntu with systemd
sudo systemctl start mongodb
```

### 2. Start Elasticsearch

```bash
# Direct execution
elasticsearch

# Or if installed via brew (macOS)
brew services start elasticsearch

# Ubuntu with systemd
sudo systemctl start elasticsearch
```

Verify Elasticsearch is running:
```bash
curl http://localhost:9200
```

### 3. Start Your LLM Provider

**If using Ollama (default):**
```bash
# Start Ollama service
ollama serve
```

In a new terminal, verify the model is available:
```bash
ollama list
```

**If using OpenAI or Gemini:**
- No service to start! Just ensure your API key is in `.env`
- Skip this step and proceed to running the application

### 4. Run the Application

**Option A: Use the helper script (Recommended)**

```bash
./run.sh
```

The helper script automatically:
- Activates virtual environment
- Checks if port 8000 is in use (and offers to kill conflicting processes)
- Verifies MongoDB, Elasticsearch, and Ollama are running
- Starts the application with hot-reload

To use a different port: `./run.sh 8080`

**Option B: Start manually**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**Tip:** Keep separate terminal windows open for MongoDB, Elasticsearch, and your LLM provider (if using Ollama) while the application is running.

**Verify Your LLM Provider:**
```bash
curl http://localhost:8000/health
```
The response will show which provider is active under `llm_provider`.

#### Troubleshooting Port Conflicts

If you get `Address already in use` error:

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 $(lsof -ti :8000)

# Or use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Usage

### Uploading Receipts

1. Navigate to http://localhost:8000
2. Drag and drop a receipt image (JPG, PNG, or PDF) into the upload zone, or click to browse
3. Wait for the AI analysis to complete
4. View the extracted receipt data

### Searching Receipts

1. Use the search bar to search across:
   - Store names
   - Product names
   - UPC codes
   - Transaction IDs

2. Apply advanced filters:
   - Store name
   - Date range
   - Price range (min/max)

3. Click "View Details" on any receipt to see full information

### API Endpoints

#### Upload Receipt
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/receipt.jpg"
```

#### Search Receipts
```bash
curl "http://localhost:8000/api/search?q=Home+Depot&min_price=50"
```

#### Get Single Receipt
```bash
curl "http://localhost:8000/api/receipts/{receipt_id}"
```

#### List All Receipts
```bash
curl "http://localhost:8000/api/receipts?skip=0&limit=20"
```

## Project Structure

```
vouch/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration with multi-provider support
│   ├── models.py                    # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_llm_service.py     # Abstract base class for LLM providers
│   │   ├── llm_factory.py          # Factory pattern for provider selection
│   │   ├── image_utils.py          # Shared image processing utilities
│   │   ├── ollama_service.py       # Ollama provider implementation
│   │   ├── openai_service.py       # OpenAI provider implementation
│   │   ├── gemini_service.py       # Google Gemini provider implementation
│   │   ├── mongodb_service.py      # MongoDB operations
│   │   └── elasticsearch_service.py # Search functionality
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py               # File upload endpoints
│   │   └── search.py               # Search endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── components/
├── uploads/                         # Temporary file storage
├── prompt.txt                       # LLM prompt template (shared by all providers)
├── receipt-breakdown-schema.json    # JSON schema
├── requirements.txt
├── .env.example
├── README.md
├── PROVIDER_SETUP_GUIDE.md         # Detailed provider setup instructions
├── IMPLEMENTATION_SUMMARY.md       # Technical implementation details
└── MIGRATION_GUIDE.md              # Migration guide for existing users
```

## Receipt Schema

Receipts are analyzed and stored with the following structure:

- **transaction_info**: Store details, date, time, cashier, transaction ID
- **items**: Array of purchased items with UPC, name, price, quantity
  - **warranty_details**: For items >= $100, includes coverage, requirements, source URL
- **totals**: Subtotal, sales tax, grand total
- **payment_info**: Card type, last four digits, authorization code
- **return_policy**: Policy ID, return window, expiration date, notes

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongosh`
- Check connection string in `.env`

### Elasticsearch Connection Issues
- Verify service is running: `curl http://localhost:9200`
- Check Elasticsearch logs for errors

### LLM Provider Issues

**Ollama:**
- Verify Ollama is running: `ollama list`
- Ensure llama3.2-vision is installed: `ollama pull llama3.2-vision`
- Check Ollama logs: `ollama serve`
- Verify URL in `.env` matches Ollama server

**OpenAI:**
- Verify API key is set in `.env`: `OPENAI_API_KEY=sk-...`
- Check API key is valid at https://platform.openai.com/api-keys
- Ensure you have sufficient credits/billing enabled
- Check for rate limit errors in logs

**Gemini:**
- Verify API key is set in `.env`: `GEMINI_API_KEY=...`
- Check API key is valid at https://makersuite.google.com/app/apikey
- Ensure you haven't exceeded free tier limits
- Check for rate limit errors in logs

**Check Active Provider:**
```bash
curl http://localhost:8000/health
```
Look for `llm_provider` field in the response.

### PDF Processing Issues
- Install poppler-utils: `brew install poppler` (macOS) or `apt-get install poppler-utils` (Ubuntu)

### Port Conflicts
If port 8000 is already in use, run on a different port:
```bash
uvicorn app.main:app --reload --port 8080
```

### Switching Providers
To switch LLM providers:
1. Update `LLM_PROVIDER` in `.env` (ollama, openai, or gemini)
2. Add the required API key if using OpenAI or Gemini
3. Restart the application
4. Verify with health check: `curl http://localhost:8000/health`

## Choosing the Right LLM Provider

### When to Use Ollama
- ✅ Privacy-sensitive data (receipts stay on your machine)
- ✅ Development and testing
- ✅ No ongoing costs
- ✅ No internet required after model download
- ⚠️ Slower on CPU (faster with GPU)
- ⚠️ Requires local setup

### When to Use OpenAI
- ✅ Production deployments requiring high accuracy
- ✅ Fast processing needed
- ✅ No local infrastructure
- ✅ Most accurate receipt parsing
- ⚠️ Costs ~$0.01-0.03 per receipt
- ⚠️ Data sent to cloud

### When to Use Gemini
- ✅ Cost optimization (free tier: 15 requests/min)
- ✅ Good balance of speed and accuracy
- ✅ No local infrastructure
- ✅ Google AI capabilities
- ⚠️ Data sent to cloud
- ⚠️ Rate limits on free tier

For detailed comparison and setup instructions, see [PROVIDER_SETUP_GUIDE.md](PROVIDER_SETUP_GUIDE.md)

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_config.py::TestSettings::test_default_settings

# Run by marker
pytest -m unit

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show slowest tests
pytest --durations=10

```

### Code Formatting
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Documentation

- **[PROVIDER_SETUP_GUIDE.md](PROVIDER_SETUP_GUIDE.md)** - Detailed setup instructions for each LLM provider
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration guide for existing Ollama users
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Support

For issues and questions, please open an issue on the GitHub repository.

### Common Issues
- **LLM shows "unhealthy"**: Check that your chosen provider is running/configured
- **API key errors**: Verify API key is set correctly in `.env`
- **Wrong provider active**: Check `LLM_PROVIDER` in `.env` and restart the app
