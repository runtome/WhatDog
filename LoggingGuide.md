# Conversation Logging Guide

## Overview

The chatbot now logs all conversations to CSV files organized by date. Each day gets its own log file in the format `DD-MM-YYYY.csv`.

## Features

✅ Automatic daily log file creation
✅ Logs text and image messages
✅ Tracks response time for each interaction
✅ Records LINE user ID, question, answer, and timestamp
✅ Two log viewers: simple and fancy

## Log Format

Each log file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `time` | Time of interaction (HH:MM:SS) | 14:30:45 |
| `line_user` | LINE user ID | U1234567890abcdef... |
| `question` | User's message or [IMAGE] filename | สวัสดี |
| `answer_reply` | Bot's response | สวัสดีครับ ยินดีที่ได้รู้จัก... |
| `response_time` | Time to generate response | 0.234s |

## Directory Structure

```
~/whatdog/
├── logs/                          # Log directory (auto-created)
│   ├── 05-02-2026.csv            # Daily log files
│   ├── 06-02-2026.csv
│   └── 07-02-2026.csv
├── images/                        # Uploaded dog images
├── main_with_logging.py          # Bot with logging enabled
└── view_logs_simple.py           # Log viewer
```

## Usage

### 1. Start the Bot with Logging

```bash
# Copy the logging version as your main file
cp main_with_logging.py main.py

# Run with waitress (production)
waitress-serve --listen=0.0.0.0:5000 main:app

# Or run with Flask (development)
python main.py
```

### 2. View Today's Logs

```bash
python view_logs_simple.py
```

### 3. View Specific Date Logs

```bash
# View logs from a specific date
python view_logs_simple.py 05-02-2026

# View yesterday's logs
python view_logs_simple.py yesterday

# View today's logs explicitly
python view_logs_simple.py today
```

### 4. List All Available Logs

```bash
python view_logs_simple.py list
```

### 5. Export Summary Report

```bash
# Export summary for today
python view_logs_simple.py export

# Export summary for specific date
python view_logs_simple.py export 05-02-2026
```

## Example Output

### Log File Content (05-02-2026.csv)

```csv
time,line_user,question,answer_reply,response_time
14:30:45,U1234567890abcdef,สวัสดี,สวัสดีครับ ยินดีที่ได้รู้จักนะครับ,0.234s
14:31:20,U1234567890abcdef,[IMAGE] 2026_02_05_14_31_20_599676723697025417.jpg,🐶 สายพันธ์น้องหมา...,2.456s
14:32:10,U9876543210fedcba,ชื่ออะไร,ผมชื่อไลน์บอทครับ...,0.189s
```

### Viewer Output

```
╔═══════════════════════════════════════════════════════════════╗
║            LINE Chatbot Log Viewer (Simple)                   ║
╚═══════════════════════════════════════════════════════════════╝

================================================================================
📊 Conversation Logs for 05-02-2026
================================================================================

[1] 14:30:45
    👤 User: U1234567890abcdef
    ❓ Question: สวัสดี
    💬 Answer: สวัสดีครับ ยินดีที่ได้รู้จักนะครับ
    ⏱️  Response Time: 0.234s
    ----------------------------------------------------------------------------

[2] 14:31:20
    👤 User: U1234567890abcdef
    ❓ Question: [IMAGE] 2026_02_05_14_31_20_599676723697025417.jpg
    💬 Answer: 🐶 สายพันธ์น้องหมา...
    ⏱️  Response Time: 2.456s
    ----------------------------------------------------------------------------

================================================================================
📈 Statistics for 05-02-2026
================================================================================
📝 Total conversations: 2
👥 Unique users: 1
💬 Text messages: 1
🖼️  Image messages: 1

⏱️  Response times:
   • Average: 1.345s
   • Fastest: 0.234s
   • Slowest: 2.456s
================================================================================
```

## Advanced: Direct CSV Analysis

You can also analyze logs directly with pandas:

```python
import pandas as pd

# Read log file
df = pd.read_csv('logs/05-02-2026.csv')

# Show first 5 rows
print(df.head())

# Get statistics
print(df.describe())

# Count messages by user
print(df['line_user'].value_counts())

# Average response time
df['response_time_float'] = df['response_time'].str.replace('s', '').astype(float)
print(f"Average response time: {df['response_time_float'].mean():.3f}s")

# Filter image messages
images = df[df['question'].str.contains('[IMAGE]')]
print(f"Total images: {len(images)}")
```

## Log Retention

Log files are kept indefinitely. To manage disk space:

```bash
# Delete logs older than 30 days
find logs/ -name "*.csv" -mtime +30 -delete

# Compress old logs
gzip logs/*.csv

# Archive logs by month
mkdir -p logs/archive/2026-02
mv logs/??-02-2026.csv logs/archive/2026-02/
```

## Privacy Considerations

⚠️ **Important:** Log files contain:
- LINE user IDs
- User messages
- Bot responses

Make sure to:
1. Keep logs directory secure
2. Don't commit logs to version control (add `logs/` to `.gitignore`)
3. Follow data retention policies
4. Implement log rotation if needed

## Troubleshooting

### Logs not being created

1. Check if `logs/` directory exists:
   ```bash
   ls -la logs/
   ```

2. Check file permissions:
   ```bash
   chmod 755 logs/
   ```

3. Check for errors in bot console output

### Can't view logs

1. Make sure you're in the correct directory:
   ```bash
   cd ~/whatdog
   ```

2. Check if log file exists:
   ```bash
   ls -l logs/
   ```

3. Try the simple viewer:
   ```bash
   python view_logs_simple.py list
   ```

## Custom Analytics

You can create custom reports by reading the CSV files:

```python
import csv
from collections import defaultdict

# Count questions by hour
hour_counts = defaultdict(int)

with open('logs/05-02-2026.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        hour = row['time'].split(':')[0]
        hour_counts[hour] += 1

# Print hourly distribution
for hour in sorted(hour_counts.keys()):
    print(f"{hour}:00 - {hour_counts[hour]} messages")
```

## Integration with Analytics Tools

Export logs to Google Sheets, Excel, or analytics platforms:

```bash
# Convert to Excel
pip install openpyxl pandas
python -c "import pandas as pd; pd.read_csv('logs/05-02-2026.csv').to_excel('logs/05-02-2026.xlsx', index=False)"
```