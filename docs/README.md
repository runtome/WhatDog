# 🐶 Dog Breed Detection LINE Chatbot with Thai LLM

A LINE chatbot that combines:
- 🐕 **Dog breed detection** using PyTorch ResNet18
- 💬 **Thai language conversation** using Thai LLM API
- 📊 **Conversation logging** to CSV files

## Features

✅ **Image Recognition**
- Upload dog photos → Get top 3 breed predictions with confidence scores
- Powered by fine-tuned ResNet18 model
- Supports 120+ dog breeds

✅ **Intelligent Chat**
- Natural Thai language conversations
- Powered by Thai LLM API (thaillm.or.th)
- Fast and context-aware responses

✅ **Logging & Analytics**
- Daily CSV logs (DD-MM-YYYY.csv)
- Track: time, user, question, answer, response time
- Built-in log viewer with statistics

## Quick Start

### 1. Setup Environment
```bash
cd ~/whatdog
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure .env
```bash
cp .env.example .env
nano .env
```

Add your credentials:
```env
# LINE Bot
CHANNEL_SECRET=your_channel_secret
CHANNEL_ACCESS_TOKEN=your_access_token

# Thai LLM API
THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=xxxxxx
THAI_LLM_MODEL=/model
```

### 3. Test Components
```bash
# Test PyTorch model
python test_model_fixed.py

# Test Thai LLM API
python test_thaillm.py

# Both should succeed ✅
```

### 4. Run Bot
```bash
# Production (recommended)
waitress-serve --listen=0.0.0.0:5000 main:app

# Development
python main.py
```

### 5. View Logs
```bash
# Today's conversations
python view_logs_simple.py

# Specific date
python view_logs_simple.py 05-02-2026

# List all logs
python view_logs_simple.py list
```

## File Structure

```
~/whatdog/
├── main.py                      # Main bot (copy from main_with_thaillm.py)
├── resnet18_best.pth           # Trained model
├── .env                        # Your credentials (DO NOT COMMIT)
├── requirements.txt            # Python dependencies
│
├── images/                     # Uploaded dog photos
│   └── 2026_02_05_14_30_45_*.jpg
│
├── logs/                       # Conversation logs
│   ├── 05-02-2026.csv
│   ├── 06-02-2026.csv
│   └── 07-02-2026.csv
│
├── test_model_fixed.py         # Test dog breed detection
├── test_thaillm.py            # Test Thai LLM API
├── view_logs_simple.py        # View conversation logs
│
└── docs/
    ├── SETUP_GUIDE.md         # Initial setup
    ├── THAILLM_GUIDE.md       # Thai LLM integration
    ├── LOGGING_GUIDE.md       # Logging documentation
    ├── MIGRATION_GUIDE.md     # Ollama → Thai LLM migration
    └── QUICK_REFERENCE.md     # Command cheatsheet
```

## How It Works

### Text Messages
```
User: สวัสดี
  ↓
Thai LLM API
  ↓
Bot: สวัสดีครับ ยินดีที่ได้รู้จัก...
  ↓
Log to CSV: 05-02-2026.csv
```

### Image Messages
```
User: [Uploads dog photo]
  ↓
PyTorch ResNet18
  ↓
Bot: 🐶 สายพันธ์น้องหมา
     1. Chihuahua (95.23%)
     2. Mexican_hairless (3.45%)
     3. toy_terrier (1.32%)
  ↓
Log to CSV: 05-02-2026.csv
```

## Available Files

### Main Files
- **main_with_thaillm.py** - Full featured bot (Thai LLM + Logging)
- **main_with_logging.py** - Dog detection + Logging only
- **main_with_ollama.py** - Dog detection + Local Ollama

### Test Scripts
- **test_model_fixed.py** - Test dog breed model
- **test_thaillm.py** - Test Thai LLM API connection

### Utilities
- **view_logs_simple.py** - Simple log viewer (no dependencies)
- **view_logs.py** - Fancy log viewer (requires tabulate)

### Documentation
- **SETUP_GUIDE.md** - Complete setup instructions
- **THAILLM_GUIDE.md** - Thai LLM API integration guide
- **LOGGING_GUIDE.md** - Logging system documentation
- **MIGRATION_GUIDE.md** - Migrate from Ollama to Thai LLM
- **QUICK_REFERENCE.md** - Quick command reference

## Configuration Options

### Thai LLM Parameters

Adjust in `main.py`:
```python
def ask_thai_llm(user_message, max_tokens=2048, temperature=0.3):
```

**max_tokens** (512 - 4096):
- Lower = Faster, shorter responses
- Higher = Slower, more detailed responses

**temperature** (0.0 - 1.0):
- 0.0 = Very focused, consistent
- 0.3 = Balanced (recommended)
- 0.7 = Creative, varied
- 1.0 = Very creative, random

### Quick Responses

Add instant responses for common questions:
```python
quick_responses = {
    "สวัสดี": "สวัสดีครับ 😊",
    "ขอบคุณ": "ยินดีครับ 🙏",
}
```

## Monitoring

### View Today's Activity
```bash
python view_logs_simple.py
```

Shows:
- Total conversations
- Unique users
- Text vs Image messages
- Average/Min/Max response times

### Export Statistics
```bash
# Export summary report
python view_logs_simple.py export

# Creates: logs/summary_DD-MM-YYYY.txt
```

### Real-time Monitoring
```bash
# Watch logs live
tail -f logs/$(date +%d-%m-%Y).csv

# Watch bot console
# (Keep terminal open when running bot)
```

## Troubleshooting

### PyTorch "could not create a primitive" ✅ FIXED
This is already fixed in all provided files with:
```python
os.environ['MKL_THREADING_LAYER'] = 'GNU'
torch.backends.mkldnn.enabled = False
```

### Thai LLM API Not Responding
```bash
# Test connection
python test_thaillm.py

# Check .env file
cat .env | grep THAI_LLM

# Manual test
curl http://thaillm.or.th/api/pathumma/v1/chat/completions \
  -H "apikey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "/model", "messages": [{"role": "user", "content": "test"}]}'
```

### Waitress "Bad module" Error
```bash
# Make sure Flask is installed
pip install flask

# Verify main.py exists
ls -l main.py

# Check if app object exists
grep "app = Flask" main.py
```

### Logs Not Creating
```bash
# Check permissions
ls -la logs/

# Create directory manually
mkdir -p logs
chmod 755 logs

# Check bot console for errors
```

## Performance

### Expected Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| Text (Quick Response) | <0.1s | Instant predefined answers |
| Text (Thai LLM) | 1-3s | API call + processing |
| Image (Dog Breed) | 0.5-2s | Model inference |
| Image (Large) | 2-5s | Download + processing |

### Optimization Tips

1. **Use Quick Responses** for common questions
2. **Reduce max_tokens** for faster Thai LLM responses
3. **Add caching** for repeated questions
4. **Monitor logs** to identify slow operations

## Security

### Protected Files (.gitignore)
```
.env              # Your credentials
logs/             # User conversations
images/           # Uploaded photos
*.pth            # Model files (optional)
```

### Best Practices
- ✅ Never commit `.env` file
- ✅ Keep logs directory private
- ✅ Rotate logs regularly
- ✅ Use environment variables for all secrets
- ✅ Monitor API usage

## Deployment

### Local Development
```bash
python main.py
# Access: http://localhost:5000
```

### Production with Waitress
```bash
waitress-serve --listen=0.0.0.0:5000 main:app
# More stable, better performance
```

### With Systemd (Auto-start)
```bash
# Create service file
sudo nano /etc/systemd/system/whatdog.service
```

```ini
[Unit]
Description=What Dog LINE Bot
After=network.target

[Service]
Type=simple
User=serverapp
WorkingDirectory=/home/serverapp/whatdog
Environment="PATH=/home/serverapp/whatdog/venv/bin"
ExecStart=/home/serverapp/whatdog/venv/bin/waitress-serve --listen=0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable whatdog
sudo systemctl start whatdog

# Check status
sudo systemctl status whatdog
```

## API Usage

### Thai LLM API
- **Rate Limit:** Check with API provider
- **Max Tokens:** 2048 (configurable)
- **Timeout:** 30 seconds
- **Cost:** Free (check current terms)

### LINE Messaging API
- **Message Limit:** Check your plan
- **Image Size:** Max 10MB
- **Response Time:** Must reply within 30 seconds

## Support

### Documentation
- 📖 [Setup Guide](SETUP_GUIDE.md)
- 🇹🇭 [Thai LLM Guide](THAILLM_GUIDE.md)
- 📊 [Logging Guide](LOGGING_GUIDE.md)
- 🔄 [Migration Guide](MIGRATION_GUIDE.md)
- ⚡ [Quick Reference](QUICK_REFERENCE.md)

### Testing
```bash
# Full test suite
python test_model_fixed.py     # PyTorch model
python test_thaillm.py          # Thai LLM API
python view_logs_simple.py list # Check logs
```

### Logs
Check console output and CSV logs in `logs/` directory

## License

This project uses:
- PyTorch (BSD License)
- LINE Bot SDK (Apache 2.0)
- Thai LLM API (Check provider terms)

## Credits

- **Dog Breed Model:** Fine-tuned ResNet18
- **Thai LLM:** thaillm.or.th
- **Framework:** Flask + LINE Bot SDK

---

## Quick Command Reference

```bash
# Start bot
waitress-serve --listen=0.0.0.0:5000 main:app

# Test systems
python test_model_fixed.py
python test_thaillm.py

# View logs
python view_logs_simple.py
python view_logs_simple.py yesterday
python view_logs_simple.py list

# Monitor live
tail -f logs/$(date +%d-%m-%Y).csv

# Check status
curl http://localhost:5000/
```

---

🎉 **Your bot is ready!** Send it text for AI chat or images for dog breed detection!
