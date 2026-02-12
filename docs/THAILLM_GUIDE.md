# Thai LLM API Integration Guide

## Overview

Your chatbot now uses **Thai LLM API** (thaillm.or.th) for intelligent text responses while keeping the dog breed detection for images.

## Features

✅ **Text Messages** → Thai LLM API (intelligent conversation in Thai)
✅ **Image Messages** → Dog Breed Detection (PyTorch model)
✅ **Conversation Logging** → CSV files per day
✅ **Response Time Tracking** → Performance monitoring

## API Configuration

### Thai LLM API Details

- **Endpoint:** `http://thaillm.or.th/api/pathumma/v1/chat/completions`
- **API Key:** `Your API KEY`
- **Model:** `/model`
- **Format:** OpenAI-compatible chat completion API

### Environment Variables

Add to your `.env` file:

```env
# Thai LLM API Configuration
THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=Your API KEY
THAI_LLM_MODEL=/model
```

## Installation & Setup

### 1. Update Environment File

```bash
cd ~/whatdog

# Copy the example .env
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your LINE credentials and Thai LLM settings:
```env
CHANNEL_SECRET=your_line_channel_secret
CHANNEL_ACCESS_TOKEN=your_line_access_token

THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=Your API KEY
THAI_LLM_MODEL=/model
```

### 2. Test the API Connection

```bash
# Test if Thai LLM API is working
python test_thaillm.py

# Or test with a custom message
python test_thaillm.py "สวัสดี คุณเป็นอย่างไรบ้าง"
```

### 3. Deploy the Bot

```bash
# Replace your main.py with the Thai LLM version
cp main_with_thaillm.py main.py

# Run with waitress (production)
waitress-serve --listen=0.0.0.0:5000 main:app
```

## How It Works

### Text Message Flow

```
User sends text → Bot receives → Thai LLM API → Response → User
                      ↓
                 Log to CSV
```

### Image Message Flow

```
User sends image → Bot receives → PyTorch Model → Dog Breed → User
                       ↓
                  Log to CSV
```

## API Request Format

```json
{
  "model": "/model",
  "messages": [
    {"role": "user", "content": "สวัสดี"}
  ],
  "max_tokens": 2048,
  "temperature": 0.3
}
```

## API Response Format

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "สวัสดีครับ ยินดีที่ได้รู้จักครับ..."
      }
    }
  ]
}
```

## Customization Options

### Adjust Response Parameters

In `main_with_thaillm.py`, modify the `ask_thai_llm()` function:

```python
def ask_thai_llm(user_message, max_tokens=2048, temperature=0.3):
    # ...
```

**Parameters:**
- `max_tokens`: Maximum length of response (default: 2048)
  - Lower = shorter responses
  - Higher = longer, more detailed responses
  
- `temperature`: Creativity level (0.0 - 1.0, default: 0.3)
  - `0.0` = Very focused, deterministic
  - `0.3` = Balanced (recommended)
  - `0.7` = More creative
  - `1.0` = Very creative, varied

### Quick Responses (Optional)

Keep some responses local for speed:

```python
quick_responses = {
    "สวัสดี": "สวัสดีครับ ยินดีที่ได้รู้จักนะครับ 😊",
    "ขอบคุณ": "ยินดีครับ 🙏",
    "ลาก่อน": "โชคดีครับ แล้วพบกันใหม่ 👋",
}
```

These respond instantly without calling the API.

## Troubleshooting

### API Not Responding

1. **Test the connection:**
   ```bash
   python test_thaillm.py
   ```

2. **Check API key:**
   ```bash
   echo $THAI_LLM_API_KEY
   ```

3. **Manual curl test:**
   ```bash
   curl http://thaillm.or.th/api/pathumma/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "apikey: Your API KEY" \
     -d '{
       "model": "/model",
       "messages": [{"role": "user", "content": "สวัสดี"}],
       "max_tokens": 2048,
       "temperature": 0.3
     }'
   ```

### Slow Responses

1. **Reduce max_tokens:**
   ```python
   ask_thai_llm(text, max_tokens=512)  # Faster, shorter responses
   ```

2. **Use quick responses** for common questions

3. **Check API response time** in logs:
   ```bash
   python view_logs_simple.py
   ```

### API Errors

Common error codes:
- `401`: Invalid API key
- `429`: Too many requests (rate limit)
- `500`: Server error
- `timeout`: Request took too long (>30 seconds)

**Fallback behavior:** If API fails, bot will display:
```
ขอโทษครับ ขณะนี้ระบบตอบคำถามไม่สามารถใช้งานได้ 🙏
คุณสามารถส่งรูปน้องหมามาให้ผมทายสายพันธุ์ได้เลยครับ 🐶
```

## Performance Optimization

### 1. Cache Common Responses

```python
# Add at top of file
from functools import lru_cache

@lru_cache(maxsize=100)
def ask_thai_llm_cached(user_message):
    return ask_thai_llm(user_message)
```

### 2. Async Processing (Advanced)

For high-traffic bots, consider async:
```python
import asyncio
import aiohttp

async def ask_thai_llm_async(user_message):
    # Async API call
    pass
```

### 3. Response Time Monitoring

Check logs for slow responses:
```bash
python view_logs_simple.py | grep "response_time"
```

## Example Interactions

### Text Conversation
```
User: สวัสดีครับ
Bot: [Thai LLM] สวัสดีครับ ยินดีที่ได้รู้จัก มีอะไรให้ช่วยไหมครับ

User: บอกเกี่ยวกับสุนัขพันธุ์ชิวาวา
Bot: [Thai LLM] ชิวาวาเป็นสุนัขพันธุ์เล็กที่สุดในโลก มีถิ่นกำเนิดจากเม็กซิโก...
```

### Image Detection
```
User: [Sends dog image]
Bot: 🐶 สายพันธ์น้องหมา
     📊มีความน่าจะเป็นดังนี้:
     1. Chihuahua (95.23%)
     2. Mexican_hairless (3.45%)
     3. toy_terrier (1.32%)
```

## Comparison: Thai LLM vs Ollama

| Feature | Thai LLM API | Ollama |
|---------|--------------|--------|
| Language | Thai-optimized | Multilingual |
| Setup | Just API key | Install locally |
| Resource | External server | Your CPU/RAM |
| Speed | Network dependent | Local (faster) |
| Cost | Free (with limits) | Free (unlimited) |
| Thai Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Recommendation:** Use Thai LLM for Thai language conversations!

## Advanced: Switching Between APIs

Create a hybrid system:

```python
def get_response(text):
    # Try Thai LLM first
    response = ask_thai_llm(text)
    if response:
        return response
    
    # Fallback to Ollama if available
    response = ask_ollama(text)
    if response:
        return response
    
    # Final fallback
    return "ส่งรูปน้องหมาได้เลยครับ 🐶"
```

## Monitoring & Analytics

### View API Usage
```bash
# Check today's conversations
python view_logs_simple.py

# Count API calls
grep "Thai LLM" logs/$(date +%d-%m-%Y).csv | wc -l

# Average response time
python view_logs_simple.py | grep "Average"
```

### Export for Analysis
```python
import pandas as pd

df = pd.read_csv('logs/05-02-2026.csv')
api_calls = df[~df['question'].str.contains('[IMAGE]')]
print(f"API calls: {len(api_calls)}")
print(f"Avg response: {api_calls['response_time'].mean()}")
```

## Support & Resources

- **Thai LLM Documentation:** http://thaillm.or.th/docs
- **API Status:** Check with `python test_thaillm.py`
- **Issue Tracking:** Check bot logs in `logs/` directory

---

🎉 Your bot now has intelligent Thai language conversation powered by Thai LLM!
