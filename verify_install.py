#!/usr/bin/env python3
"""
Verification script to check if all dependencies are installed correctly.
Run this after: pip install -r requirements.txt
"""

import sys
from importlib import import_module

REQUIRED_PACKAGES = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("jinja2", "Jinja2"),
    ("motor", "Motor (MongoDB async driver)"),
    ("pymongo", "PyMongo"),
    ("elasticsearch", "Elasticsearch"),
    ("httpx", "HTTPX"),
    ("dotenv", "python-dotenv"),
    ("PIL", "Pillow"),
    ("pypdf", "pypdf"),
    ("pdf2image", "pdf2image"),
    ("pydantic", "Pydantic"),
    ("pydantic_settings", "Pydantic Settings"),
    ("jsonschema", "jsonschema"),
    ("aiofiles", "aiofiles"),
    ("multipart", "python-multipart"),
]


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✓ Python version is compatible (3.11+)")
        return True
    else:
        print("✗ Python version should be 3.11 or higher")
        return False


def check_packages():
    """Check if all required packages are installed."""
    print("\nChecking required packages:")
    all_good = True

    for package_name, display_name in REQUIRED_PACKAGES:
        try:
            import_module(package_name)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name} - NOT FOUND")
            all_good = False

    return all_good


def check_app_imports():
    """Check if app modules can be imported."""
    print("\nChecking application modules:")
    try:
        from app.config import settings
        print(f"✓ app.config - Settings loaded")

        from app.models import Receipt
        print(f"✓ app.models - Models loaded")

        from app.services.ollama_service import OllamaService
        print(f"✓ app.services.ollama_service - Service loaded")

        from app.services.mongodb_service import MongoDBService
        print(f"✓ app.services.mongodb_service - Service loaded")

        from app.services.elasticsearch_service import ElasticsearchService
        print(f"✓ app.services.elasticsearch_service - Service loaded")

        return True
    except Exception as e:
        print(f"✗ Failed to import app modules: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Vouch Installation Verification")
    print("=" * 60)

    python_ok = check_python_version()
    packages_ok = check_packages()
    app_ok = check_app_imports()

    print("\n" + "=" * 60)
    if python_ok and packages_ok and app_ok:
        print("✓ All checks passed! Installation is ready.")
        print("\nNext steps:")
        print("1. Start MongoDB: brew services start mongodb-community")
        print("2. Start Elasticsearch: brew services start elasticsearch")
        print("3. Start Ollama: ollama serve")
        print("4. Run app: uvicorn app.main:app --reload")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("- Create fresh venv: python -m venv venv")
        print("- Activate venv: source venv/bin/activate")
        print("- Upgrade pip: pip install --upgrade pip")
        print("- Install deps: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
