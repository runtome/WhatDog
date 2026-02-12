# PythonAnywhere Deployment Guide

## Why This Version?

**Problem:** PyTorch + torchvision = ~1.1GB, but PythonAnywhere free tier only has 512MB RAM
**Solution:** Use ONNX Runtime instead = ~15MB + dependencies = ~100-150MB total

### Size Comparison

| Component | PyTorch Version | ONNX Version |
|-----------|----------------|--------------|
| ML Framework | torch (~800MB) + torchvision (~300MB) | onnxruntime (~15MB) |
| Dependencies | ~100MB | ~80MB |
| **Total** | **~1.2GB** ❌ | **~100MB** ✅ |

---

## Step-by-Step Deployment

### Phase 1: Local Preparation (On Your Computer)

#### 1.1 Convert Model to ONNX Format

Run this **locally** where you have PyTorch installed:

```bash
# Make sure you're in the directory with resnet18_best.pth
python convert_to_onnx.py
```

This will create `dog_breed_model.onnx` (~45MB file).

**Output:**
```
✅ SUCCESS! Model exported to: dog_breed_model.onnx
📊 File Sizes:
   Original PyTorch (.pth): 44.65 MB
   ONNX (.onnx): 44.70 MB
```

#### 1.2 Test ONNX Model Locally (Optional)

```bash
# Install onnxruntime locally
pip install onnxruntime

# Test the converted model
python -c "
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession('dog_breed_model.onnx')
dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
outputs = session.run(None, {'input': dummy_input})
print('✅ ONNX model works!')
print(f'Output shape: {outputs[0].shape}')
"
```

---

### Phase 2: PythonAnywhere Setup

#### 2.1 Create Account

1. Go to https://www.pythonanywhere.com
2. Sign up for a **free account**
3. Confirm your email

#### 2.2 Upload Files

**Method 1: Using Web Interface**

1. Go to **Files** tab
2. Navigate to `/home/yourusername/`
3. Create directory: `whatdog`
4. Upload these files:
   - `dog_breed_model.onnx` (converted model)
   - `main_pythonanywhere.py` (rename to `main.py`)
   - `.env` (with your credentials)
   - `requirements_pythonanywhere.txt` (rename to `requirements.txt`)

**Method 2: Using Git** (recommended)

```bash
# In PythonAnywhere Bash console
cd ~
git clone https://github.com/yourusername/whatdog.git
cd whatdog

# Or upload files via SCP/SFTP
```

#### 2.3 Install Dependencies

Open a **Bash console** in PythonAnywhere:

```bash
cd ~/whatdog

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import onnxruntime; print('✅ onnxruntime installed')"
python -c "from PIL import Image; print('✅ Pillow installed')"
python -c "import numpy; print('✅ numpy installed')"
```

#### 2.4 Configure .env File

Create or edit `.env` file:

```bash
nano .env
```

Add your credentials:
```env
CHANNEL_SECRET=your_channel_secret_here
CHANNEL_ACCESS_TOKEN=your_access_token_here

THAI_LLM_URL=http://thaillm.or.th/api/pathumma/v1/chat/completions
THAI_LLM_API_KEY=Your API KEY
THAI_LLM_MODEL=/model
```

#### 2.5 Test Locally First

```bash
cd ~/whatdog
source venv/bin/activate

# Test the ONNX model
python -c "
import onnxruntime as ort
session = ort.InferenceSession('dog_breed_model.onnx')
print('✅ Model loaded successfully')
"

# Test main.py imports
python -c "
import main
print('✅ Main file imports successfully')
"
```

---

### Phase 3: Web App Configuration

#### 3.1 Create Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**

#### 3.2 Configure WSGI File

1. In **Web** tab, click on WSGI configuration file
2. Replace content with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/whatdog'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Import Flask app
from main import app as application
```

**Replace `yourusername` with your actual PythonAnywhere username!**

#### 3.3 Configure Virtual Environment

1. In **Web** tab, find **Virtualenv** section
2. Enter path: `/home/yourusername/whatdog/venv`
3. Click the checkmark

#### 3.4 Set Working Directory

In WSGI file, ensure working directory is set:

```python
# Change to project directory
os.chdir(project_home)
```

#### 3.5 Reload Web App

1. Scroll to top of **Web** tab
2. Click green **Reload** button
3. Wait for reload to complete

---

### Phase 4: Configure LINE Webhook

#### 4.1 Get Your PythonAnywhere URL

Your app will be at: `https://yourusername.pythonanywhere.com`

#### 4.2 Set LINE Webhook URL

1. Go to LINE Developers Console
2. Select your bot
3. In **Messaging API** tab:
   - Webhook URL: `https://yourusername.pythonanywhere.com/`
   - Enable **Use webhook**
   - Disable **Auto-reply messages**
   - Enable **Webhooks**

#### 4.3 Verify Webhook

Click **Verify** button in LINE Console
- Should show: ✅ Success

---

### Phase 5: Testing

#### 5.1 Test Web Endpoint

```bash
curl https://yourusername.pythonanywhere.com/
# Should return: "Hello Line Chatbot - PythonAnywhere Edition"
```

#### 5.2 Test via LINE App

1. Add your bot as friend in LINE
2. Send text message: "สวัสดี"
   - Should reply: "สวัสดีครับ ยินดีที่ได้รู้จักนะครับ 😊"
3. Send dog image
   - Should reply with breed predictions + info

#### 5.3 Check Logs

In PythonAnywhere:

1. Go to **Web** tab
2. Click **Log files** → **Error log**
3. Check for any errors

Or via Bash:
```bash
tail -f /var/log/yourusername.pythonanywhere.com.error.log
tail -f /var/log/yourusername.pythonanywhere.com.server.log
```

---

## Troubleshooting

### Issue: "No module named 'onnxruntime'"

**Solution:**
```bash
cd ~/whatdog
source venv/bin/activate
pip install onnxruntime
```

### Issue: "Model file not found"

**Solution:**
```bash
cd ~/whatdog
ls -lh dog_breed_model.onnx
# Should show the file (~45MB)
```

If missing, upload `dog_breed_model.onnx` to `/home/yourusername/whatdog/`

### Issue: "Memory error" or "Killed"

**Possible causes:**
1. Free tier has 512MB limit
2. Multiple processes running

**Solution:**
```bash
# Check memory usage
free -h

# Kill old processes
ps aux | grep python
kill -9 <PID>
```

### Issue: LINE webhook verification fails

**Check:**
1. Is web app running? (Green "Reload" button in Web tab)
2. Is WSGI file configured correctly?
3. Is virtual environment path correct?
4. Are logs showing errors?

```bash
# Test endpoint directly
curl https://yourusername.pythonanywhere.com/
```

### Issue: Bot doesn't respond

**Check:**
1. Error logs in Web tab
2. Is `.env` file present and correct?
3. Are LINE credentials correct?

```bash
# Check .env file
cd ~/whatdog
cat .env

# Test imports
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('CHANNEL_SECRET'))"
```

---

## Memory Optimization Tips

### 1. Disable Logging (saves ~10MB)

In `main.py`, comment out log functions:
```python
# log_conversation(...)  # Comment out
```

### 2. Reduce Image Storage

```python
# Don't save images to disk
# with open(image_path, "wb") as img_file:  # Comment out
#     for chunk in message_content.iter_content(chunk_size=1024):
#         img_file.write(chunk)
```

### 3. Limit Concurrent Requests

PythonAnywhere free tier has limits:
- 1 web worker
- 100 seconds CPU time per day
- 512MB RAM

### 4. Use Smaller Images

If memory is tight, resize images before inference:
```python
# In preprocess_image(), use smaller size
image = image.resize((112, 112), Image.BILINEAR)  # Half size
```

---

## Monitoring

### Check Resource Usage

```bash
# Bash console
free -h
df -h
du -sh ~/whatdog/*
```

### View Logs

```bash
# Application logs
tail -f ~/whatdog/logs/$(date +%d-%m-%Y).csv

# Error logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log
```

---

## Updating the Bot

### Update Code

```bash
cd ~/whatdog
source venv/bin/activate

# Edit files
nano main.py

# Reload web app
# Go to Web tab → Click Reload
```

### Update Model

1. Convert new model locally: `python convert_to_onnx.py`
2. Upload new `dog_breed_model.onnx` to PythonAnywhere
3. Reload web app

---

## Alternative: Heroku (if PythonAnywhere doesn't work)

If you need more memory, consider:
- **Heroku** (512MB free tier)
- **Railway** (512MB free tier)
- **Render** (512MB free tier)

All support larger apps than PythonAnywhere.

---

## Comparison: PythonAnywhere vs Local Server

| Feature | PythonAnywhere | Your Server |
|---------|----------------|-------------|
| Memory | 512MB (free) | Unlimited |
| CPU | Limited | Unlimited |
| Cost | Free | Server costs |
| Setup | Easy | Complex |
| Maintenance | Minimal | You manage |
| Framework | ONNX Runtime | PyTorch |

---

## File Structure on PythonAnywhere

```
/home/yourusername/whatdog/
├── main.py                      # main_pythonanywhere.py renamed
├── dog_breed_model.onnx        # Converted ONNX model (~45MB)
├── .env                        # Your credentials
├── requirements.txt            # requirements_pythonanywhere.txt renamed
├── venv/                       # Virtual environment
├── logs/                       # Conversation logs (auto-created)
│   └── DD-MM-YYYY.csv
└── images/                     # Uploaded images (optional)
    └── *.jpg
```

---

## Success Checklist

- [ ] ONNX model converted locally
- [ ] Files uploaded to PythonAnywhere
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] WSGI file configured
- [ ] Web app reloaded
- [ ] LINE webhook configured
- [ ] Webhook verification successful
- [ ] Text message test passed
- [ ] Image message test passed
- [ ] Logs working

---

🎉 **Your bot is now running on PythonAnywhere with only ~100MB memory usage!**
