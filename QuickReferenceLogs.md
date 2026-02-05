# 📊 Quick Reference: Conversation Logging

## File Structure
```
logs/
├── 05-02-2026.csv    # Today's conversations
├── 04-02-2026.csv    # Yesterday's conversations
└── 03-02-2026.csv    # Older logs
```

## Quick Commands

### View Logs
```bash
# Today
python view_logs_simple.py

# Yesterday  
python view_logs_simple.py yesterday

# Specific date
python view_logs_simple.py 05-02-2026

# List all
python view_logs_simple.py list
```

### Start Bot with Logging
```bash
# Run
waitress-serve --listen=0.0.0.0:5000 main_with_ollama:app
```

## CSV Format
```csv
time,line_user,question,answer_reply,response_time
14:30:45,U1234...,สวัสดี,สวัสดีครับ...,0.234s
14:31:20,U1234...,[IMAGE] filename.jpg,🐶 สายพันธ์...,2.456s
```

## What Gets Logged?

✅ **Text Messages**
- Time: HH:MM:SS
- User ID: LINE user identifier
- Question: User's text message
- Answer: Bot's response
- Response Time: Processing time in seconds

✅ **Image Messages**
- Question: `[IMAGE] filename.jpg`
- Answer: Dog breed predictions
- Response Time: Including image processing

## Log Viewer Features

📊 **Statistics Shown:**
- Total conversations
- Unique users
- Text vs Image count
- Average/Min/Max response time

## Privacy & Security

⚠️ **Important:**
- Logs contain user IDs and messages
- Add `logs/` to `.gitignore`
- Set proper file permissions
- Implement log rotation for production

## Troubleshooting

**Logs not created?**
```bash
ls -la logs/
chmod 755 logs/
```

**Can't view logs?**
```bash
cd ~/whatdog
python view_logs_simple.py list
```

**Need to clean old logs?**
```bash
# Delete logs older than 30 days
find logs/ -name "*.csv" -mtime +30 -delete
```

## Advanced Usage

**Read with Python:**
```python
import csv
with open('logs/05-02-2026.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['time'], row['question'])
```

**Read with pandas:**
```python
import pandas as pd
df = pd.read_csv('logs/05-02-2026.csv')
print(df.describe())
```

**Convert to Excel:**
```python
import pandas as pd
pd.read_csv('logs/05-02-2026.csv').to_excel('report.xlsx')
```

---

💡 **Tip:** Run `python view_logs_simple.py` daily to monitor bot usage!