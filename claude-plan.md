# Vouch - Receipt Analysis Application Implementation Plan

## Overview
Build a full-stack Python application using FastAPI for receipt upload, Ollama vision analysis, MongoDB storage, and Elasticsearch search functionality.

## Architecture Decisions
- **Backend**: FastAPI (async, modern, automatic API docs)
- **Frontend**: Jinja2 templates with HTMX for dynamic search
- **Vision AI**: Ollama with llama3.2-vision model
- **Storage**: MongoDB for JSON document storage
- **Search**: Elasticsearch for full-text search and indexing
- **File Handling**: Store uploaded files temporarily, 5MB limit, JPG/PNG/PDF only

## Project Structure
```
vouch/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ollama_service.py  # Ollama API client
│   │   ├── mongodb_service.py # MongoDB operations
│   │   └── elasticsearch_service.py # Elasticsearch operations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py          # File upload endpoints
│   │   └── search.py          # Search endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       ├── base.html
│       ├── index.html          # Main page with upload & search
│       └── components/
│           └── receipt_card.html
├── uploads/                     # Temporary upload directory
├── prompt.txt                   # Existing LLM prompt
├── receipt-breakdown-schema.json # Existing JSON schema
├── requirements.txt
├── .env.example
└── README.md
```

## Implementation Steps

### 1. Project Setup
**Files**: `requirements.txt`, `.env.example`, `app/__init__.py`

Dependencies to add:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `python-multipart` - File upload support
- `jinja2` - Template engine
- `aiofiles` - Async file operations
- `motor` - Async MongoDB driver
- `elasticsearch[async]` - Async Elasticsearch client
- `httpx` - Async HTTP client for Ollama API
- `python-dotenv` - Environment variable management
- `Pillow` - Image processing
- `PyPDF2` or `pdf2image` - PDF handling
- `pydantic-settings` - Settings management
- `jsonschema` - JSON validation against schema

Create `.env.example` with:
- `MONGODB_URL`
- `ELASTICSEARCH_URL`
- `OLLAMA_API_URL`
- `OLLAMA_MODEL`
- `MAX_UPLOAD_SIZE`
- `UPLOAD_DIR`

### 2. Configuration Management
**File**: `app/config.py`

Create Pydantic Settings class to manage:
- Service URLs (MongoDB, Elasticsearch, Ollama)
- File upload settings (max size, allowed extensions, upload directory)
- Model configuration (llama3.2-vision)
- CORS settings if needed

### 3. Data Models
**File**: `app/models.py`

Define Pydantic models based on `receipt-breakdown-schema.json`:
- `TransactionInfo`
- `Item` (with optional `WarrantyDetails`)
- `Totals`
- `PaymentInfo`
- `ReturnPolicy`
- `Receipt` (main model combining all above)
- `UploadResponse`
- `SearchQuery`
- `SearchResult`

### 4. Ollama Service
**File**: `app/services/ollama_service.py`

Implement `OllamaService` class:
- `analyze_receipt(image_path: str) -> dict`:
  - Read `prompt.txt` file
  - Send image to Ollama API with llama3.2-vision
  - Handle JPG/PNG directly
  - Convert PDF to image first page
  - Parse JSON response
  - Validate against schema using `jsonschema`
  - Return structured receipt data

Key considerations:
- Use `httpx.AsyncClient` for async API calls
- Handle Ollama API errors gracefully
- Support multimodal input (text prompt + image)
- Extract and validate JSON from LLM response

### 5. MongoDB Service
**File**: `app/services/mongodb_service.py`

Implement `MongoDBService` class:
- `connect()`: Initialize Motor client and get database/collection
- `save_receipt(receipt_data: dict) -> str`: Insert receipt, return ID
- `get_receipt(receipt_id: str) -> dict`: Retrieve single receipt
- `get_all_receipts(skip: int, limit: int) -> list`: Paginated list
- `search_receipts_by_store(store_name: str) -> list`: Filter by store
- `disconnect()`: Close connection

Collection: `receipts`
Indexes:
- `transaction_info.store_name`
- `transaction_info.date_purchased`
- `items.product_name`

### 6. Elasticsearch Service
**File**: `app/services/elasticsearch_service.py`

Implement `ElasticsearchService` class:
- `connect()`: Initialize async Elasticsearch client
- `create_index()`: Create `receipts` index with mapping
- `index_receipt(receipt_id: str, receipt_data: dict)`: Index document
- `search(query: str, filters: dict) -> list`: Full-text search
  - Search across: store_name, product_name, UPC, transaction_id
  - Support filters by date range, price range, store
  - Return matched receipts with highlights
- `disconnect()`: Close connection

Index mapping:
- Transaction info fields as keywords/text
- Items nested objects with text search on product_name
- Numeric fields for range queries (prices, dates)

### 7. Upload Router
**File**: `app/routers/upload.py`

Endpoints:
- `POST /api/upload`: Handle file upload
  - Validate file type (JPG, PNG, PDF only)
  - Validate file size (max 5MB)
  - Save to temporary directory
  - Call OllamaService to analyze
  - Save to MongoDB
  - Index in Elasticsearch
  - Delete temporary file
  - Return receipt ID and analyzed data
  - Handle errors appropriately

### 8. Search Router
**File**: `app/routers/search.py`

Endpoints:
- `GET /api/search`: Search receipts
  - Query params: `q` (search term), `store`, `date_from`, `date_to`, `min_price`, `max_price`
  - Call ElasticsearchService.search()
  - Enrich with MongoDB data if needed
  - Return JSON results
- `GET /api/receipts/{receipt_id}`: Get single receipt detail
- `GET /api/receipts`: List all receipts (paginated)

### 9. Main Application
**File**: `app/main.py`

FastAPI application setup:
- Initialize FastAPI app
- Configure Jinja2Templates
- Mount static files
- Include routers (upload, search)
- Lifespan context manager for service connections:
  - Connect to MongoDB on startup
  - Connect to Elasticsearch on startup
  - Create Elasticsearch index if not exists
  - Disconnect on shutdown
- Root route (`GET /`) serving index.html template
- Health check endpoint (`GET /health`)

### 10. Frontend Templates
**Files**: `app/templates/base.html`, `app/templates/index.html`, `app/templates/components/receipt_card.html`

`base.html`:
- Basic HTML structure
- Include HTMX via CDN
- Link to styles.css
- Navigation/header

`index.html`:
- Upload section with drag-and-drop zone
- File validation client-side
- Progress indicator during upload/analysis
- Search bar with filters (store, date range, price)
- Results container for HTMX updates
- Success/error message display

`components/receipt_card.html`:
- Reusable receipt display component
- Show transaction info, items, totals
- Click to view full details
- Highlight warranty items

### 11. Static Assets
**Files**: `app/static/css/styles.css`, `app/static/js/app.js`

`styles.css`:
- Clean, responsive design
- Upload zone styling (drag-and-drop visual feedback)
- Receipt card grid layout
- Search filters styling
- Loading states

`app.js`:
- File validation before upload
- HTMX event handlers
- Search debouncing
- Dynamic filter updates

### 12. Documentation Updates
**File**: `README.md`

Update with:
- Prerequisites (Python 3.11+, MongoDB, Elasticsearch, Ollama)
- Installation steps
- Service setup instructions:
  - Start MongoDB: `mongod --dbpath /path/to/db`
  - Start Elasticsearch: `elasticsearch`
  - Start Ollama with llama3.2-vision: `ollama pull llama3.2-vision && ollama serve`
- Environment configuration (copy .env.example to .env)
- Run application: `uvicorn app.main:app --reload`
- Access at `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`

## Critical Files
- `app/main.py` - Application entry point
- `app/services/ollama_service.py` - Vision AI integration
- `app/services/mongodb_service.py` - Data persistence
- `app/services/elasticsearch_service.py` - Search functionality
- `app/routers/upload.py` - File upload and processing
- `app/routers/search.py` - Search API
- `app/templates/index.html` - Main UI
- `requirements.txt` - Dependencies

## Verification Steps

### 1. Service Connectivity
- Verify MongoDB connection: Check health endpoint returns MongoDB status
- Verify Elasticsearch connection: Check index creation
- Verify Ollama connection: Test with sample image

### 2. File Upload Testing
- Upload JPG receipt: Should analyze and return JSON
- Upload PNG receipt: Should analyze and return JSON
- Upload PDF receipt: Should convert and analyze
- Test file size limit: 6MB file should be rejected
- Test invalid file type: .txt file should be rejected

### 3. Analysis Validation
- Check JSON output matches schema
- Verify items with price >= $100 include warranty lookup
- Confirm data saved to MongoDB
- Confirm data indexed in Elasticsearch

### 4. Search Testing
- Search by store name: Should return matching receipts
- Search by product name: Should find items across receipts
- Search by UPC: Should find specific products
- Test date range filter: Should filter by purchase date
- Test price range filter: Should filter by item/total price

### 5. UI Testing
- Access http://localhost:8000
- Upload receipt via drag-and-drop
- View analysis results
- Perform search queries
- Apply filters
- View receipt details

### 6. Error Handling
- Test with corrupted image
- Test with non-receipt image
- Test with Ollama service down
- Test with MongoDB connection failure
- Test with Elasticsearch unavailable

## Success Criteria
- ✓ File upload works with size and type validation
- ✓ Ollama analyzes receipts and returns structured JSON
- ✓ JSON validates against receipt-breakdown-schema.json
- ✓ Data persists to MongoDB
- ✓ Data indexes in Elasticsearch
- ✓ Search returns relevant results
- ✓ UI displays receipts and search works
- ✓ Items >= $100 include warranty information
- ✓ Error handling provides clear feedback
