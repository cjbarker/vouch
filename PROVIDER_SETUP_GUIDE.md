# Multi-Provider LLM Setup Guide

## Quick Start

The Vouch application now supports three LLM providers for receipt analysis. Choose the one that best fits your needs.

## Provider Comparison

| Provider | Cost | Privacy | Setup Complexity | API Key Required |
|----------|------|---------|------------------|-----------------|
| **Ollama** | Free (self-hosted) | High (local) | Medium | No |
| **OpenAI** | Pay-per-use | Low (cloud) | Easy | Yes |
| **Gemini** | Free tier + paid | Low (cloud) | Easy | Yes |

## Setup Instructions

### Option 1: Ollama (Default - Local & Private)

**Pros:** Free, private, no API key needed
**Cons:** Requires local setup, slower on CPU

1. Install Ollama:
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull a vision model:
   ```bash
   ollama pull llama3.2-vision
   ```

3. Start Ollama:
   ```bash
   ollama serve
   ```

4. Configure `.env`:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_API_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2-vision
   ```

5. Start the app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Option 2: OpenAI (Cloud - Most Accurate)

**Pros:** Most accurate, fast, easy setup
**Cons:** Costs money, sends data to cloud

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)

2. Configure `.env`:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-...your-key-here...
   OPENAI_MODEL=gpt-4-vision-preview
   OPENAI_MAX_TOKENS=4096
   OPENAI_TEMPERATURE=0.0
   ```

3. Start the app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

**Cost:** ~$0.01-0.03 per receipt (varies by complexity)

### Option 3: Google Gemini (Cloud - Free Tier)

**Pros:** Free tier available, fast, good accuracy
**Cons:** Sends data to cloud, rate limits on free tier

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Configure `.env`:
   ```bash
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=...your-key-here...
   GEMINI_MODEL=gemini-1.5-pro-vision
   GEMINI_TEMPERATURE=0.0
   ```

3. Start the app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

**Cost:** Free tier: 15 RPM, 1500 RPD. Paid: varies.

## Switching Providers

You can switch providers at any time by changing the `LLM_PROVIDER` environment variable and restarting the application.

### Method 1: Edit `.env` file
```bash
# Change this line in .env
LLM_PROVIDER=openai  # or ollama, or gemini
```

### Method 2: Environment variable
```bash
export LLM_PROVIDER=openai
python -m uvicorn app.main:app --reload
```

### Method 3: Docker
```bash
docker run -e LLM_PROVIDER=openai -e OPENAI_API_KEY=sk-... vouch:latest
```

## Verifying Your Setup

### Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "mongodb": "healthy",
    "elasticsearch": "healthy",
    "llm": "healthy",
    "llm_provider": "ollama"
  }
}
```

The `llm_provider` field shows which provider is currently active.

### Test Receipt Upload

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/receipt.jpg"
```

## Troubleshooting

### Error: "OPENAI_API_KEY is required"
- **Solution:** Add `OPENAI_API_KEY=sk-...` to your `.env` file

### Error: "GEMINI_API_KEY is required"
- **Solution:** Add `GEMINI_API_KEY=...` to your `.env` file

### Error: "Failed to connect to Ollama"
- **Solution:** Make sure Ollama is running: `ollama serve`
- **Check:** Verify URL in `.env` matches Ollama server

### LLM shows "unhealthy" in health check
- **Ollama:** Check if `ollama serve` is running
- **OpenAI:** Verify API key is valid
- **Gemini:** Verify API key is valid

### Receipt analysis returns errors
- **Check logs:** Look for specific error messages
- **Verify image:** Ensure image is clear and under 5MB
- **Test provider:** Use health check endpoint to verify provider is working

## Recommended Models

### Ollama
- **llama3.2-vision** (default) - Best balance of speed and accuracy
- **llava** - Alternative, slightly faster
- **bakllava** - Older, less accurate

### OpenAI
- **gpt-4-vision-preview** (default) - Most accurate
- **gpt-4o** - Faster, good accuracy
- **gpt-4-turbo** - Good balance

### Gemini
- **gemini-1.5-pro-vision** (default) - Best accuracy
- **gemini-1.5-flash** - Faster, slightly less accurate
- **gemini-pro-vision** - Older model

## Performance Tips

1. **For Development:** Use Ollama (free, private)
2. **For Production (High Volume):** Use OpenAI or Gemini (faster, more reliable)
3. **For Privacy-Sensitive Data:** Use Ollama (everything stays local)
4. **For Cost Optimization:** Use Gemini free tier, then Ollama
5. **For Best Accuracy:** Use OpenAI gpt-4-vision-preview

## Environment Variable Reference

```bash
# Provider Selection
LLM_PROVIDER=ollama|openai|gemini

# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-vision-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.0

# Gemini Configuration
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro-vision
GEMINI_TEMPERATURE=0.0
```

## Next Steps

1. Choose your provider based on your needs (privacy, cost, accuracy)
2. Follow the setup instructions for your chosen provider
3. Test with the health check endpoint
4. Upload a test receipt
5. Monitor performance and switch providers if needed

## Support

For issues or questions:
- Check the logs: Look for error messages in the application output
- Verify configuration: Ensure all required environment variables are set
- Test health endpoint: Confirm services are running
- Review API limits: Check if you've hit rate limits (for cloud providers)
