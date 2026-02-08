# Requirements.txt Analysis Report

Generated: 2026-02-07

## Summary

**Total Packages:** 89
**Direct Dependencies:** ~18
**Transitive Dependencies:** ~65
**Development Tools:** 3
**Potentially Unused:** 3

## Direct Dependencies (Used in Code)

These packages are explicitly imported and used in the application:

| Package | Purpose | Used In |
|---------|---------|---------|
| **fastapi** | Web framework | main.py, routers |
| **uvicorn** | ASGI server | Running the app |
| **python-multipart** | File upload handling | FastAPI file uploads |
| **jinja2** | Template engine | HTML templates |
| **motor** | MongoDB async driver | mongodb_service.py |
| **pymongo** | MongoDB sync driver | Required by motor, bson imports |
| **elasticsearch** | Search engine client | elasticsearch_service.py |
| **httpx** | HTTP client | ollama_service.py |
| **python-dotenv** | Environment variables | config.py |
| **Pillow** | Image processing | Image handling in services |
| **pypdf** | PDF reading | PDF processing |
| **pdf2image** | PDF to image conversion | image_utils.py |
| **pydantic** | Data validation | models.py |
| **pydantic-settings** | Settings management | config.py |
| **jsonschema** | JSON schema validation | upload.py |
| **openai** | OpenAI API client | openai_service.py |
| **google-genai** | Google Gemini API client | gemini_service.py |

## Transitive Dependencies (Required by Direct Dependencies)

These packages are automatically installed as dependencies of the direct packages:

### FastAPI/Starlette Ecosystem
- **starlette** - Required by FastAPI
- **anyio** - Async I/O, required by FastAPI/Starlette
- **sniffio** - Async library detection, required by anyio
- **h11** - HTTP/1.1 implementation, required by uvicorn
- **httptools** - Fast HTTP parser, required by uvicorn
- **websockets** - WebSocket support, required by uvicorn
- **watchfiles** - File watching, required by uvicorn --reload
- **uvloop** - Fast event loop, required by uvicorn

### Pydantic Ecosystem
- **pydantic_core** - Pydantic core validation
- **typing_extensions** - Typing extensions
- **annotated-types** - Annotated types support

### HTTP/Network Libraries
- **httpcore** - HTTP core, required by httpx
- **certifi** - SSL certificates
- **idna** - Internationalized domain names
- **charset-normalizer** - Character encoding detection

### MongoDB/Motor
- **dnspython** - DNS resolver for MongoDB SRV records

### Elasticsearch
- **elastic-transport** - Transport layer for elasticsearch

### Google Gemini Dependencies
- **google-api-core** - Google API core utilities
- **google-auth** - Google authentication
- **google-auth-httplib2** - HTTP library for auth
- **google-api-python-client** - Google API client
- **googleapis-common-protos** - Google API protocol buffers
- **proto-plus** - Protocol buffers plus
- **protobuf** - Protocol buffers
- **grpcio** - gRPC library
- **grpcio-status** - gRPC status codes
- **google-ai-generativelanguage** - Generative AI language API
- **httplib2** - HTTP library
- **uritemplate** - URI template processing
- **pyasn1** - ASN.1 support
- **pyasn1_modules** - ASN.1 modules

### OpenAI Dependencies
- **aiohttp** - Async HTTP client
- **aiohappyeyeballs** - Happy eyeballs for aiohttp
- **aiosignal** - Async signals
- **frozenlist** - Frozen list implementation
- **multidict** - Multi-value dictionary
- **yarl** - URL parsing
- **propcache** - Property caching
- **attrs** - Classes without boilerplate
- **jiter** - JSON iterator
- **distro** - Linux distribution info
- **tqdm** - Progress bars

### Testing/Utilities
- **tenacity** - Retry library (used by openai)
- **requests** - HTTP library
- **urllib3** - HTTP client
- **six** - Python 2/3 compatibility

### Other Transitive
- **MarkupSafe** - Safe string handling, required by Jinja2
- **click** - Command line interface, required by various tools
- **cryptography** - Cryptographic recipes
- **cffi** - Foreign function interface
- **pycparser** - C parser
- **packaging** - Package version handling
- **pyparsing** - Parsing library
- **python-dateutil** - Date utilities
- **referencing** - JSON schema referencing
- **rpds-py** - Rust-powered data structures
- **typing-inspection** - Runtime type inspection

## Development Tools

These are used for development, not runtime:

| Package | Purpose | Status |
|---------|---------|--------|
| **black** | Code formatter | ✓ Used |
| **pytest** | Testing framework | ⚠️ No tests found |
| **mypy_extensions** | Type checking | ⚠️ mypy not used currently |
| **Pygments** | Syntax highlighting | ⚠️ Used by some dev tools |
| **iniconfig** | INI file parsing (pytest) | Transitive |
| **pluggy** | Plugin system (pytest) | Transitive |
| **pathspec** | Path pattern matching (black) | Transitive |
| **platformdirs** | Platform directories (black) | Transitive |

## Potentially Unused or Redundant Packages

### 🔴 REDUNDANT - Should Remove

1. **google-generativeai==0.8.6**
   - **Status:** DEPRECATED and REDUNDANT
   - **Reason:** We're using the new `google-genai` package instead
   - **Action:** Remove this line from requirements.txt
   - **Note:** This is the old, deprecated SDK that shows warnings

2. **PyPDF2==3.0.1**
   - **Status:** REDUNDANT
   - **Reason:** We're using `pypdf` (the newer version), not PyPDF2
   - **Action:** Remove this line from requirements.txt
   - **Note:** pypdf is the successor to PyPDF2

### 🟡 UNUSED - Consider Removing

3. **aiofiles==25.1.0**
   - **Status:** NOT IMPORTED in code
   - **Reason:** Listed but not actually used anywhere in the codebase
   - **Action:** Remove unless you plan to use it for async file operations
   - **Note:** Could be useful for future optimizations

4. **PyYAML==6.0.3**
   - **Status:** NOT IMPORTED in code
   - **Reason:** No YAML files or yaml imports found
   - **Action:** Remove unless needed for configuration
   - **Note:** Common to add "just in case" but not actually needed

5. **pytokens==0.4.1**
   - **Status:** NOT IMPORTED in code
   - **Reason:** No usage found
   - **Action:** Remove
   - **Note:** Unclear why this was added

6. **annotated-doc==0.0.4**
   - **Status:** NOT IMPORTED in code
   - **Reason:** No usage found
   - **Action:** Remove
   - **Note:** May have been added for documentation but not used

## Recommended Actions

### High Priority (Redundant Packages)

Remove these immediately as they're redundant:

```bash
# Current requirements.txt has:
google-generativeai==0.8.6  # ❌ REMOVE - Using google-genai instead
PyPDF2==3.0.1              # ❌ REMOVE - Using pypdf instead
```

### Medium Priority (Unused Packages)

Consider removing these if not planned for future use:

```bash
aiofiles==25.1.0           # ❌ REMOVE - Not imported anywhere
PyYAML==6.0.3              # ❌ REMOVE - No YAML usage
pytokens==0.4.1            # ❌ REMOVE - Not used
annotated-doc==0.0.4       # ❌ REMOVE - Not used
```

### Testing Infrastructure

The project has pytest installed but no tests:

```bash
# Directory structure lacks:
tests/                     # ❌ Missing test directory
test_*.py files           # ❌ No test files found
conftest.py               # ❌ No pytest configuration
```

**Recommendation:** Either:
1. Keep pytest and write tests (recommended)
2. Remove pytest if not planning to test

## Optimized requirements.txt

Here's a cleaned-up version with only necessary packages:

```python
# Web Framework
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
python-multipart>=0.0.9
jinja2>=3.1.3

# Database & Search
motor>=3.4.0
pymongo>=4.6.2
elasticsearch[async]==8.12.0

# LLM Providers
httpx>=0.27.0              # Ollama
openai>=1.10.0             # OpenAI
google-genai>=0.1.0        # Gemini (NEW SDK)

# Configuration & Validation
python-dotenv>=1.0.1
pydantic>=2.6.0
pydantic-settings>=2.2.1
jsonschema>=4.21.1

# File Processing
Pillow>=10.2.0
pypdf>=4.0.0               # PDF reading (new version)
pdf2image>=1.17.0

# Development Tools
black>=26.1.0              # Code formatting
pytest>=9.0.2              # Testing (if writing tests)
```

## Size Reduction Estimate

Removing redundant/unused packages could save:
- **google-generativeai**: ~50MB (deprecated SDK)
- **PyPDF2**: ~5MB (redundant)
- **aiofiles**: ~1MB
- **PyYAML**: ~5MB
- **pytokens**: ~1MB
- **annotated-doc**: ~1MB

**Total potential savings: ~63MB**

## Version Pinning Analysis

Current approach uses `==` (exact pinning) for all packages. This:

### Advantages
- ✓ Reproducible builds
- ✓ No surprise updates
- ✓ Stable production environment

### Disadvantages
- ✗ No security updates
- ✗ Requires manual updates
- ✗ Can cause dependency conflicts

### Recommendation

Use `>=` with upper bounds for direct dependencies:
```python
fastapi>=0.110.0,<1.0.0
openai>=1.10.0,<3.0.0
```

And use `pip freeze > requirements.lock` for deployment.

## Conclusion

The requirements.txt file contains:
- ✅ **17 essential direct dependencies** - All actively used
- ✅ **~65 transitive dependencies** - Required by direct deps
- ⚠️ **2 redundant packages** - Remove immediately
- ⚠️ **4 unused packages** - Consider removing
- ⚠️ **Testing tools** - Installed but no tests exist

**Action Items:**
1. Remove `google-generativeai` (using new SDK)
2. Remove `PyPDF2` (using pypdf instead)
3. Consider removing: aiofiles, PyYAML, pytokens, annotated-doc
4. Either write tests or remove pytest
5. Consider using `>=` version pinning strategy
