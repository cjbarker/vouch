# Requirements Management Guide

## File Structure

### `requirements.txt` (Clean, Minimal)
**Purpose:** Direct dependencies with version ranges
**Use:** Development and fresh installations
**Format:** Only packages you explicitly need (24 packages)

```bash
pip install -r requirements.txt
```

### `requirements.lock` (Frozen, Complete)
**Purpose:** Exact versions of all packages (including transitive)
**Use:** Production deployments for reproducibility
**Format:** Output of `pip freeze` (89 packages)

```bash
pip install -r requirements.lock
```

## What Was Removed

### ❌ Redundant Packages
- **google-generativeai** - Deprecated SDK, using `google-genai` instead
- **PyPDF2** - Old library, using `pypdf` instead

### ❌ Unused Packages
- **aiofiles** - Not imported anywhere
- **PyYAML** - No YAML usage
- **pytokens** - Not used
- **annotated-doc** - Not used

### ✅ Transitive Dependencies
~59 packages removed from requirements.txt but will be auto-installed by pip:
- starlette, anyio, httpcore (FastAPI dependencies)
- google-auth, grpcio, protobuf (Gemini dependencies)
- aiohttp, attrs, tenacity (OpenAI dependencies)
- etc.

These don't need to be listed explicitly!

## Version Strategy

### Before (Exact Pinning)
```python
fastapi==0.128.0
```
- ✓ Reproducible builds
- ✗ No security updates
- ✗ Hard to maintain

### After (Range Constraints)
```python
fastapi>=0.110.0
```
- ✓ Security updates allowed
- ✓ Easier maintenance
- ✓ More flexible
- Use `requirements.lock` for exact versions in production

## Usage Scenarios

### Development
```bash
# Install with latest compatible versions
pip install -r requirements.txt

# Add new package
pip install new-package
echo "new-package>=1.0.0" >> requirements.txt
```

### Testing Changes
```bash
# Test with new versions
pip install -r requirements.txt --upgrade

# Generate new lock file if all works
pip freeze > requirements.lock
```

### Production
```bash
# Install exact versions for reproducibility
pip install -r requirements.lock
```

### After Adding New Dependency
```bash
# 1. Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# 2. Install it
pip install new-package

# 3. Update lock file
pip freeze > requirements.lock
```

## Categories in requirements.txt

### Web Framework
FastAPI, Uvicorn, Jinja2, python-multipart

### Database & Search
Motor, PyMongo, Elasticsearch

### LLM Providers
- httpx (Ollama)
- openai (OpenAI)
- google-genai (Gemini)

### Configuration & Validation
Pydantic, python-dotenv, jsonschema

### File Processing
Pillow, pypdf, pdf2image

### Development Tools
black, pytest

## Benefits of New Structure

### Before
```python
# 89 packages
# Unclear what's direct vs transitive
# Hard to update
# No categories
```

### After
```python
# 24 direct dependencies
# Clear organization
# Easy to update
# Commented by purpose
# Security updates possible
```

## Dependency Tree Example

```
requirements.txt lists:
  fastapi>=0.110.0
    ├── starlette (auto-installed)
    ├── pydantic (listed separately)
    └── typing-extensions (auto-installed)

  openai>=1.10.0
    ├── httpx (listed separately for Ollama)
    ├── aiohttp (auto-installed)
    └── tqdm (auto-installed)
```

You only need to list `fastapi` and `openai`!

## Checking for Unused Dependencies

```bash
# Install pip-autoremove
pip install pip-autoremove

# Check what can be removed
pip-autoremove --leaves

# Or use pipdeptree
pip install pipdeptree
pipdeptree --reverse
```

## Regenerating Lock File

```bash
# After testing new versions
pip freeze > requirements.lock

# Commit both files
git add requirements.txt requirements.lock
git commit -m "Update dependencies"
```

## Best Practices

1. **Keep requirements.txt minimal** - Only direct dependencies
2. **Use version ranges** - Allow security updates
3. **Test before locking** - Ensure compatibility
4. **Update lock file** - After successful testing
5. **Use lock in production** - For reproducibility
6. **Document dev tools** - Make it clear they're optional

## Troubleshooting

### "Module not found" error
```bash
# Reinstall from clean requirements
pip install -r requirements.txt
```

### Version conflicts
```bash
# Check dependency tree
pip install pipdeptree
pipdeptree

# Fix conflicts by adjusting version ranges
```

### Production deployment fails
```bash
# Use lock file for exact versions
pip install -r requirements.lock
```

## Size Comparison

```
requirements.lock:  89 packages (~500MB installed)
requirements.txt:   24 packages (~500MB installed)

Same installed size, but:
- requirements.txt is easier to read
- requirements.txt is easier to maintain
- requirements.lock ensures reproducibility
```

## Migration from Old Requirements

The old frozen requirements.txt has been saved as `requirements.lock`.

If you need to rollback:
```bash
mv requirements.lock requirements.txt
pip install -r requirements.txt
```

## Summary

- ✅ **requirements.txt** - Clean, minimal, maintained by humans
- ✅ **requirements.lock** - Complete, frozen, generated by `pip freeze`
- ✅ Both files committed to git
- ✅ Development uses requirements.txt
- ✅ Production uses requirements.lock
