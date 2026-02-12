# Migration Guide: Ollama → Thai LLM API

## What Changed?

### Before (Ollama)
```python
def ask_ollama(prompt, model=None):
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=30
    )
    return response.json().get("response")
```

### After (Thai LLM)
```python
def ask_thai_llm(user_message, max_tokens=2048, temperature=0.3):
    headers = {
        "Content-Type": "application/json",
        "apikey": thai_llm_api_key
    }
    
    payload = {
        "model": thai_llm_model,
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    response = requests.post(thai_llm_url, headers=headers, json=payload)
    result = response.json()
    return result['choices'][0]['message']['content']
```

## Key Differences

| Feature | Ollama | Thai LLM API |
|---------|--------|--------------|
| **Request Format** | Simple prompt string | OpenAI-style messages array |
| **Authentication** | None (local) | API key in header |
| **Response Format** | Direct string | Nested JSON structure |
| **Endpoint** | `/api/generate` | `/api/chat/completions` |
| **Headers** | Just Content-Type | Content-Type + apikey |

## Environment Variables Comparison

### Ollama (.env)
```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

### Thai LLM (.env)
```env
THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=Your API KEY
THAI_LLM_MODEL=/model
```

## Migration Steps

### 1. Update .env File
```bash
cd ~/whatdog
nano .env
```

Add Thai LLM configuration:
```env
THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=Your API KEY
THAI_LLM_MODEL=/model
```

### 2. Test the API
```bash
python test_thaillm.py "สวัสดี"
```

### 3. Replace Main File
```bash
# Backup old version (optional)
cp main.py main_ollama_backup.py

# Use Thai LLM version
cp main_with_thaillm.py main.py
```

### 4. Restart Bot
```bash
# Stop current bot (Ctrl+C)

# Start with new version
waitress-serve --listen=0.0.0.0:5000 main:app
```

## Request/Response Examples

### Ollama Request
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "สวัสดี",
  "stream": false
}'
```

**Response:**
```json
{
  "response": "สวัสดีครับ..."
}
```

### Thai LLM Request
```bash
curl http://thaillm.or.th/api/pathumma/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "apikey: Your API KEY" \
  -d '{
    "model": "/model",
    "messages": [
      {"role": "user", "content": "สวัสดี"}
    ],
    "max_tokens": 2048,
    "temperature": 0.3
  }'
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "สวัสดีครับ..."
      }
    }
  ]
}
```

## Code Changes Breakdown

### 1. Import Changes
No changes needed - both use `requests`

### 2. Environment Variables
```python
# OLD
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

# NEW
thai_llm_url = os.getenv("THAI_LLM_URL", "http://thaillm.or.th/api/pathumma/v1/chat/completions")
thai_llm_api_key = os.getenv("THAI_LLM_API_KEY", "Your API KEY")
thai_llm_model = os.getenv("THAI_LLM_MODEL", "/model")
```

### 3. Function Changes
```python
# OLD
def ask_ollama(prompt, model=None):
    if model is None:
        model = ollama_model
    
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response")
    return None

# NEW
def ask_thai_llm(user_message, max_tokens=2048, temperature=0.3):
    headers = {
        "Content-Type": "application/json",
        "apikey": thai_llm_api_key
    }
    
    payload = {
        "model": thai_llm_model,
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    response = requests.post(
        thai_llm_url,
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
    return None
```

### 4. Usage in Handler
```python
# OLD
ollama_response = ask_ollama(text)
if ollama_response:
    reply_text = ollama_response

# NEW
llm_response = ask_thai_llm(text)
if llm_response:
    reply_text = llm_response
```

## Advantages of Thai LLM

✅ **Better Thai Language Understanding**
- Optimized for Thai conversations
- Better grammar and context

✅ **No Local Installation**
- No need to install Ollama
- No need to download large models
- Saves disk space (1-3GB)

✅ **External Processing**
- Doesn't use your CPU/RAM
- Server can handle multiple requests

✅ **Always Updated**
- Model improvements happen server-side
- No manual updates needed

## Keeping Both (Hybrid Approach)

You can keep both and use as fallback:

```python
def get_ai_response(text):
    # Try Thai LLM first
    response = ask_thai_llm(text)
    if response:
        return response
    
    # Fallback to Ollama if installed
    response = ask_ollama(text)
    if response:
        return response
    
    # Final fallback
    return "ส่งรูปน้องหมาได้เลยครับ 🐶"
```

## Rollback Plan

If you need to go back to Ollama:

```bash
# Restore backup
cp main_ollama_backup.py main.py

# Make sure Ollama is running
ollama serve

# Restart bot
waitress-serve --listen=0.0.0.0:5000 main:app
```

## Testing Checklist

- [ ] `.env` file updated with Thai LLM credentials
- [ ] `test_thaillm.py` runs successfully
- [ ] Bot responds to Thai text messages
- [ ] Bot still detects dog breeds from images
- [ ] Logs are created in `logs/` directory
- [ ] Response times are acceptable (<5 seconds)

## Common Issues

### Issue: "No response from API"
**Solution:** Check API key and internet connection
```bash
python test_thaillm.py
```

### Issue: "Slow responses"
**Solution:** Reduce max_tokens
```python
ask_thai_llm(text, max_tokens=512)  # Faster
```

### Issue: "API key error"
**Solution:** Verify in .env
```bash
grep THAI_LLM_API_KEY .env
```

---

🎉 **Migration Complete!** Your bot now uses Thai LLM API for intelligent Thai conversations.
