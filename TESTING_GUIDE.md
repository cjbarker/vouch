# Testing Guide - Vouch Application

## Overview

This document describes the test suite for the Vouch receipt analysis application. The test suite uses **pytest** with support for async testing, mocking, and coverage reporting.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_config.py                 # Configuration tests ✅
├── test_models.py                 # Model validation tests ⚠️
├── services/
│   ├── __init__.py
│   ├── test_image_utils.py       # Image utility tests ✅
│   ├── test_llm_factory.py       # LLM factory tests ✅
│   ├── test_ollama_service.py    # Ollama service tests ✅
│   ├── test_openai_service.py    # OpenAI service tests ✅
│   └── test_gemini_service.py    # Gemini service tests ✅
└── routers/
    ├── __init__.py
    ├── test_upload.py             # Upload router tests ⚠️
    └── test_search.py             # Search router tests ⚠️
```

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_config.py -v
```

### By Marker
```bash
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "not slow"             # Exclude slow tests
```

### Verbose Output
```bash
pytest -v --tb=short
```

## Test Dependencies

```bash
pytest>=9.0.2           # Test framework
pytest-asyncio>=0.21.0  # Async test support
pytest-cov>=4.1.0       # Coverage reporting
pytest-mock>=3.12.0     # Mocking support
```

## Current Test Status

### ✅ Fully Working Tests (19 passing)

#### Configuration Tests (12 tests)
- ✅ LLMProvider enum values
- ✅ Default settings
- ✅ Provider-specific configurations (Ollama, OpenAI, Gemini)
- ✅ File upload configuration
- ✅ Allowed extensions list
- ✅ Upload directory creation
- ✅ Custom settings override

#### Image Utils Tests (5 tests)
- ✅ Convert JPG/PNG to base64
- ✅ Handle nonexistent files
- ✅ PDF conversion error handling
- ⏭️ PDF conversion (skipped - requires poppler)

#### LLM Factory Tests (3 tests - partial)
- ✅ Create Ollama service
- ✅ Factory initialization
- ⚠️ OpenAI/Gemini tests need fixture updates

### ⚠️ Tests Needing Updates

#### Model Tests (18 tests)
**Status:** Need to align with actual model schemas

**Issues:**
- Field name mismatches (e.g., `transaction_date` vs `date_purchased`)
- Missing required fields in test data
- SearchQuery uses `q` not `query`

**Action:** Update test data in `conftest.py` and `test_models.py`

#### Service Tests
**Status:** Core structure complete, mocking needs refinement

**Coverage:**
- ✅ Ollama service structure
- ✅ OpenAI service structure
- ✅ Gemini service structure
- ⚠️ Need async mocking improvements

#### Router Tests
**Status:** Integration test framework ready

**Coverage:**
- ⚠️ Upload endpoint tests (need service mocking)
- ⚠️ Search endpoint tests (need service mocking)

## Test Fixtures

### Core Fixtures (in `conftest.py`)

```python
@pytest.fixture
def test_settings()
    # Test configuration with safe defaults

@pytest.fixture
def sample_receipt_data()
    # Complete receipt data for testing

@pytest.fixture
def sample_image_path(tmp_path)
    # Creates temporary test image

@pytest.fixture
def mock_httpx_client()
    # Mocked HTTP client for Ollama

@pytest.fixture
def mock_openai_client()
    # Mocked OpenAI client

@pytest.fixture
def mock_genai_client()
    # Mocked Gemini client

@pytest.fixture
def mock_mongodb_client()
    # Mocked MongoDB client

@pytest.fixture
def mock_elasticsearch_client()
    # Mocked Elasticsearch client
```

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.unit
def test_something():
    # Unit test

@pytest.mark.integration
def test_api_endpoint():
    # Integration test

@pytest.mark.slow
def test_long_running():
    # Slow test

@pytest.mark.requires_services
def test_with_real_db():
    # Needs MongoDB/Elasticsearch running

@pytest.mark.llm
def test_llm_provider():
    # LLM-specific test
```

## Coverage Goals

Current coverage focus areas:

1. **Configuration**: 100% ✅
2. **Models**: Validation logic
3. **Services**: Core business logic
4. **Routers**: API endpoints
5. **Utilities**: Helper functions

Target: 80%+ coverage for core application code

## Writing New Tests

### Unit Test Example

```python
def test_configuration_value():
    """Test configuration setting."""
    settings = Settings()
    assert settings.llm_provider == LLMProvider.OLLAMA
```

### Async Test Example

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Mock Example

```python
def test_with_mock(mock_httpx_client):
    """Test with mocked HTTP client."""
    # Mock is already configured in conftest.py
    service = OllamaService()
    # Test code here
```

### Integration Test Example

```python
@pytest.mark.integration
def test_upload_endpoint(test_client):
    """Test upload endpoint."""
    response = test_client.post(
        "/api/upload",
        files={"file": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
```

## Mocking Strategy

### External Services

Always mock external dependencies:
- ✅ MongoDB (motor)
- ✅ Elasticsearch
- ✅ HTTP clients (httpx, openai, genai)
- ✅ File system operations (use tmp_path)

### LLM Providers

Mock all LLM API calls:
```python
@pytest.fixture
def mock_llm_service():
    service = AsyncMock()
    service.analyze_receipt.return_value = {...}
    return service
```

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
pytest tests/ -v
black app/ tests/
```

### CI Pipeline
```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
```

## Troubleshooting

### Import Errors
```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Async Test Failures
```bash
# Check pytest-asyncio is installed
pip list | grep pytest-asyncio
```

### Coverage Not Working
```bash
# Install coverage plugin
pip install pytest-cov

# Generate HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Fixture Not Found
```bash
# Check conftest.py is in tests/ directory
ls tests/conftest.py
```

## Best Practices

1. **One Assert Per Test**: Focus tests on single behaviors
2. **Use Fixtures**: Reuse common test data
3. **Mock External Services**: Never call real APIs in tests
4. **Test Edge Cases**: Test both success and failure paths
5. **Clear Test Names**: Use descriptive names like `test_upload_invalid_file_type`
6. **Arrange-Act-Assert**: Structure tests clearly
7. **Async Tests**: Use `@pytest.mark.asyncio` for async functions
8. **Cleanup**: Use `tmp_path` fixture for temporary files

## Quick Reference

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

## Next Steps

### Priority 1: Fix Model Tests
- [ ] Update `sample_receipt_data` fixture with correct field names
- [ ] Add all required fields per models.py
- [ ] Run: `pytest tests/test_models.py -v`

### Priority 2: Complete Service Tests
- [ ] Improve async mocking for LLM services
- [ ] Add error scenario tests
- [ ] Run: `pytest tests/services/ -v`

### Priority 3: Integration Tests
- [ ] Set up test database fixtures
- [ ] Add end-to-end workflow tests
- [ ] Run: `pytest -m integration`

### Priority 4: Coverage
- [ ] Achieve 80%+ coverage
- [ ] Generate and review coverage report
- [ ] Run: `pytest --cov=app --cov-report=html`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Summary

✅ **19 tests passing** - Core functionality tested
⚠️ **Test infrastructure complete** - Ready for expansion
📝 **Clear next steps** - Model tests need field name fixes
🎯 **Goal**: 80%+ code coverage with comprehensive test suite
