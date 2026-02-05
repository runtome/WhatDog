# Dog Breed Chatbot Setup Guide

## 1. Fix Virtual Environment and Install Dependencies

```bash
# Make sure you're in your project directory
cd ~/whatdog

# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

## 2. Update .env File

Add this to your `.env` file:
```
CHANNEL_SECRET=your_channel_secret_here
CHANNEL_ACCESS_TOKEN=your_access_token_here

# Optional: Ollama settings (if you want AI chat)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

## 3. Running with Waitress (Production)

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run with waitress (production server)
waitress-serve --listen=0.0.0.0:5000 main:app
```

## 4. Running with Flask (Development)

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run with Flask dev server
python main.py
```

## 5. Installing Ollama (Optional - for AI Text Chat)

### Install Ollama:
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### Download a lightweight model:
```bash
# Recommended lightweight models for CPU:
ollama pull llama3.2:1b          # 1.3GB - Very fast, good for chat
ollama pull phi3.5:3.8b          # 2.2GB - Slightly better quality
ollama pull gemma2:2b            # 1.6GB - Good balance

# Start Ollama service (usually starts automatically)
ollama serve
```

### Test Ollama:
```bash
# Test if Ollama is working
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

## 6. File Structure

Your project should look like this:
```
~/whatdog/
├── venv/                    # Virtual environment
├── images/                  # Saved dog images
├── main.py                  # Main bot file (basic version)
├── main_with_ollama.py      # Bot with AI chat (if using Ollama)
├── resnet18_best.pth        # Your trained model
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── test_model_fixed.py      # Test script
```

## 7. Which File to Use?

**Without Ollama (Dog breed only):**
```bash
waitress-serve --listen=0.0.0.0:5000 main:app
```

**With Ollama (Dog breed + AI chat):**
```bash
# First rename the file
mv main_with_ollama.py main.py

# Then run
waitress-serve --listen=0.0.0.0:5000 main:app
```

## 8. Troubleshooting

### "No module named 'flask'" error:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Ollama not responding:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### NNPACK warnings (safe to ignore):
These are harmless warnings. The model still works correctly.

## 9. Monitoring

### Check if the server is running:
```bash
curl http://localhost:5000/
# Should return: "Hello Line Chatbot"
```

### View logs:
The server will print logs to console. Keep the terminal open to see them.

## 10. Recommended Ollama Models for CPU

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.2:1b | 1.3GB | ⚡⚡⚡ | ⭐⭐ | Quick chat, fast responses |
| phi3.5:3.8b | 2.2GB | ⚡⚡ | ⭐⭐⭐ | Better understanding |
| gemma2:2b | 1.6GB | ⚡⚡⚡ | ⭐⭐⭐ | Best balance |
| qwen2.5:1.5b | 934MB | ⚡⚡⚡ | ⭐⭐ | Fastest, smallest |

For CPU servers, I recommend starting with **llama3.2:1b** or **gemma2:2b**.

## 11. Create a service for your Waitress app

### Create service file:
```bash
sudo nano /etc/systemd/system/whatdog.service
```

### Paste this (adjust paths if needed)
```bash
[Unit]
Description=Whatdog Flask App (Waitress)
After=network.target

[Service]
User=serverapp
WorkingDirectory=/home/serverapp/whatdog
ExecStart=/home/serverapp/.venv/bin/waitress-serve --listen=0.0.0.0:5000 main:app
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
⚠️ If you’re not using venv, change ExecStart to:

```bash
/usr/bin/waitress-serve --listen=0.0.0.0:5000 main:app
```

### Enable & start
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatdog
sudo systemctl start whatdog
```

### View logs (this is your “screen”)
```bash
journalctl -u whatdog -f
```

## 12. Create a service for ngrok

### Create service file:
```bash
sudo nano /etc/systemd/system/ngrok.service
```

### Paste this (adjust paths if needed)
```bash
[Unit]
Description=ngrok Tunnel
After=network.target

[Service]
User=serverapp
ExecStart=/usr/local/bin/ngrok http 5000
Restart=always

[Install]
WantedBy=multi-user.target
```
If ngrok is elsewhere:

```bash
which ngrok
```
### Enable & start
```bash
sudo systemctl daemon-reload
sudo systemctl enable ngrok
sudo systemctl start ngrok
```

### View logs (this is your “screen”)
```bash
journalctl -u ngrok -f
```
