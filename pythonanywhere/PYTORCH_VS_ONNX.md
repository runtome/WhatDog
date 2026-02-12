# PyTorch vs ONNX Runtime: Quick Comparison

## Memory Requirements

| Version | Framework | Total Size | PythonAnywhere Compatible? |
|---------|-----------|------------|---------------------------|
| **Original** | PyTorch + torchvision | ~1.2 GB | ❌ No (512MB limit) |
| **ONNX** | ONNX Runtime | ~100 MB | ✅ Yes (fits in 512MB) |

---

## What Changed?

### Code Changes

| Component | PyTorch Version | ONNX Version |
|-----------|----------------|--------------|
| **Import** | `import torch`<br>`import torchvision` | `import onnxruntime as ort`<br>`import numpy as np` |
| **Model Loading** | `torch.load('model.pth')`<br>`model.eval()` | `ort.InferenceSession('model.onnx')` |
| **Image Preprocessing** | `transforms.Compose([...])` | `numpy` operations |
| **Inference** | `with torch.no_grad():`<br>`outputs = model(input)` | `outputs = session.run(None, {'input': data})` |
| **Softmax** | `F.softmax(outputs, dim=1)` | `numpy` softmax |

### Files Needed

**For Local Server (PyTorch):**
- `resnet18_best.pth` (PyTorch model)
- `main_enhanced.py`
- PyTorch + torchvision installed

**For PythonAnywhere (ONNX):**
- `dog_breed_model.onnx` (converted model)
- `main_pythonanywhere.py`
- onnxruntime installed

---

## Step-by-Step Migration

### Local Server → PythonAnywhere

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Convert Model (ON YOUR LOCAL COMPUTER)         │
├─────────────────────────────────────────────────────────┤
│ python convert_to_onnx.py                              │
│                                                         │
│ Input:  resnet18_best.pth (PyTorch)                    │
│ Output: dog_breed_model.onnx (ONNX)                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Upload to PythonAnywhere                       │
├─────────────────────────────────────────────────────────┤
│ Upload files:                                           │
│ - dog_breed_model.onnx                                  │
│ - main_pythonanywhere.py → rename to main.py           │
│ - requirements_pythonanywhere.txt → requirements.txt   │
│ - .env                                                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Install Dependencies                           │
├─────────────────────────────────────────────────────────┤
│ python3 -m venv venv                                    │
│ source venv/bin/activate                                │
│ pip install -r requirements.txt                         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Configure Web App                              │
├─────────────────────────────────────────────────────────┤
│ 1. Create web app (Manual config, Python 3.10)         │
│ 2. Set WSGI file                                        │
│ 3. Set virtualenv path                                  │
│ 4. Reload web app                                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Configure LINE Webhook                         │
├─────────────────────────────────────────────────────────┤
│ URL: https://yourusername.pythonanywhere.com/          │
└─────────────────────────────────────────────────────────┘
```

---

## Feature Comparison

| Feature | PyTorch Version | ONNX Version |
|---------|----------------|--------------|
| Dog breed detection | ✅ Yes | ✅ Yes |
| Thai LLM chat | ✅ Yes | ✅ Yes |
| Think tag filtering | ✅ Yes | ✅ Yes |
| Auto breed info | ✅ Yes | ✅ Yes |
| Conversation logging | ✅ Yes | ✅ Yes |
| Accuracy | ✅ Same | ✅ Same |
| Speed | ✅ Fast | ✅ Slightly faster |
| Memory usage | ❌ High (1.2GB) | ✅ Low (100MB) |
| PythonAnywhere | ❌ No | ✅ Yes |

---

## Performance Comparison

### Inference Speed

| Operation | PyTorch (GPU) | PyTorch (CPU) | ONNX Runtime (CPU) |
|-----------|---------------|---------------|-------------------|
| Model loading | 2-3s | 3-5s | 0.5-1s ✅ |
| Image preprocessing | 0.01s | 0.01s | 0.01s |
| Inference (single image) | 0.05s | 0.5-1s | 0.3-0.7s ✅ |
| Softmax | 0.001s | 0.01s | 0.01s |
| **Total** | **~0.1s** | **~1s** | **~0.5s** ✅ |

ONNX Runtime is actually **faster** on CPU than PyTorch!

---

## Code Examples

### PyTorch Version

```python
import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn

# Load model
model = models.resnet18(weights='IMAGENET1K_V1')
model.fc = nn.Linear(512, 120)
model.load_state_dict(torch.load('model.pth'))
model.eval()

# Preprocess
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
input_tensor = transform(image).unsqueeze(0)

# Inference
with torch.no_grad():
    outputs = model(input_tensor)
    probs = F.softmax(outputs, dim=1)
```

### ONNX Version

```python
import onnxruntime as ort
import numpy as np
from PIL import Image

# Load model
session = ort.InferenceSession('model.onnx')

# Preprocess (manual)
image = image.resize((224, 224))
img_array = np.array(image, dtype=np.float32) / 255.0
img_array = (img_array - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
img_array = np.transpose(img_array, (2, 0, 1))
img_array = np.expand_dims(img_array, axis=0)

# Inference
outputs = session.run(None, {'input': img_array.astype(np.float32)})
probs = np.exp(outputs[0]) / np.sum(np.exp(outputs[0]), axis=1, keepdims=True)
```

---

## Which Version Should You Use?

### Use PyTorch Version When:
✅ You have your own server with >2GB RAM
✅ You want GPU acceleration
✅ You're doing model training/fine-tuning
✅ You need PyTorch-specific features
✅ Memory is not a concern

### Use ONNX Version When:
✅ Deploying to PythonAnywhere
✅ Memory is limited (512MB)
✅ You want faster CPU inference
✅ You want smaller deployment size
✅ You only need inference (not training)

---

## Troubleshooting

### Common Issues

| Issue | PyTorch | ONNX |
|-------|---------|------|
| "Out of memory" | Common on small servers | Rare |
| "Model file too large" | .pth files are big | .onnx files similar size |
| "Slow inference" | Slow on CPU | Faster on CPU |
| "Complex setup" | Many dependencies | Fewer dependencies |

### Solutions

**PyTorch "Out of Memory":**
```python
# Use ONNX version instead
```

**ONNX "Model not found":**
```bash
# Make sure you converted the model first
python convert_to_onnx.py
```

**ONNX "Wrong output shape":**
```python
# Check input preprocessing matches PyTorch version
```

---

## File Sizes

### Dependencies

**PyTorch:**
```
torch-2.0.0.whl         ~800 MB
torchvision-0.15.0.whl  ~300 MB
numpy-1.24.0.whl        ~15 MB
pillow-10.0.0.whl       ~3 MB
─────────────────────────────
Total:                  ~1118 MB ❌
```

**ONNX:**
```
onnxruntime-1.16.0.whl  ~15 MB
numpy-1.24.0.whl        ~15 MB
pillow-10.0.0.whl       ~3 MB
─────────────────────────────
Total:                  ~33 MB ✅
```

### Model Files

Both are similar:
- `resnet18_best.pth`: ~45 MB
- `dog_breed_model.onnx`: ~45 MB

---

## Quick Decision Matrix

```
Need GPU acceleration? 
├─ Yes → Use PyTorch version
└─ No  → Continue

Have >1GB RAM?
├─ Yes → Use PyTorch version (easier)
└─ No  → Use ONNX version

Deploying to PythonAnywhere?
└─ Yes → Must use ONNX version

Want fastest setup?
└─ Use ONNX version (fewer dependencies)
```

---

## Summary

| Aspect | Winner | Reason |
|--------|--------|--------|
| **Memory** | ONNX ✅ | 10x smaller |
| **Speed (CPU)** | ONNX ✅ | Optimized for CPU |
| **Speed (GPU)** | PyTorch | GPU support |
| **Setup** | ONNX ✅ | Fewer dependencies |
| **Features** | Tie | Same functionality |
| **Accuracy** | Tie | Same model |
| **PythonAnywhere** | ONNX ✅ | Only option |

**Recommendation for PythonAnywhere: Use ONNX Version** 🎉
