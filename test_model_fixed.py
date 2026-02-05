"""
Updated diagnostic script with MKL-DNN fix
Run this to verify the fix works
"""

import os
# CRITICAL: Set these BEFORE importing torch
os.environ['MKL_THREADING_LAYER'] = 'GNU'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision import models
import torch.nn as nn
import torch.nn.functional as F

# Disable MKL-DNN
torch.backends.mkldnn.enabled = False

# Define class names
class_names = ['Afghan_hound', 'African_hunting_dog', 'Airedale', 'American_Staffordshire_terrier', 
               'Appenzeller', 'Australian_terrier', 'Bedlington_terrier', 'Bernese_mountain_dog', 
               'Blenheim_spaniel', 'Border_collie', 'Border_terrier', 'Boston_bull', 'Bouvier_des_Flandres', 
               'Brabancon_griffon', 'Brittany_spaniel', 'Cardigan', 'Chesapeake_Bay_retriever', 'Chihuahua', 
               'Dandie_Dinmont', 'Doberman', 'English_foxhound', 'English_setter', 'English_springer', 
               'EntleBucher', 'Eskimo_dog', 'French_bulldog', 'German_shepherd', 'German_short-haired_pointer', 
               'Gordon_setter', 'Great_Dane', 'Great_Pyrenees', 'Greater_Swiss_Mountain_dog', 'Ibizan_hound', 
               'Irish_setter', 'Irish_terrier', 'Irish_water_spaniel', 'Irish_wolfhound', 'Italian_greyhound', 
               'Japanese_spaniel', 'Kerry_blue_terrier', 'Labrador_retriever', 'Lakeland_terrier', 'Leonberg', 
               'Lhasa', 'Maltese_dog', 'Mexican_hairless', 'Newfoundland', 'Norfolk_terrier', 'Norwegian_elkhound', 
               'Norwich_terrier', 'Old_English_sheepdog', 'Pekinese', 'Pembroke', 'Pomeranian', 'Rhodesian_ridgeback', 
               'Rottweiler', 'Saint_Bernard', 'Saluki', 'Samoyed', 'Scotch_terrier', 'Scottish_deerhound', 
               'Sealyham_terrier', 'Shetland_sheepdog', 'Shih-Tzu', 'Siberian_husky', 'Staffordshire_bullterrier', 
               'Sussex_spaniel', 'Tibetan_mastiff', 'Tibetan_terrier', 'Walker_hound', 'Weimaraner', 
               'Welsh_springer_spaniel', 'West_Highland_white_terrier', 'Yorkshire_terrier', 'affenpinscher', 
               'basenji', 'basset', 'beagle', 'black-and-tan_coonhound', 'bloodhound', 'bluetick', 'borzoi', 
               'boxer', 'briard', 'bull_mastiff', 'cairn', 'chow', 'clumber', 'cocker_spaniel', 'collie', 
               'curly-coated_retriever', 'dhole', 'dingo', 'flat-coated_retriever', 'giant_schnauzer', 
               'golden_retriever', 'groenendael', 'keeshond', 'kelpie', 'komondor', 'kuvasz', 'malamute', 
               'malinois', 'miniature_pinscher', 'miniature_poodle', 'miniature_schnauzer', 'otterhound', 
               'papillon', 'pug', 'redbone', 'schipperke', 'silky_terrier', 'soft-coated_wheaten_terrier', 
               'standard_poodle', 'standard_schnauzer', 'toy_poodle', 'toy_terrier', 'vizsla', 'whippet', 
               'wire-haired_fox_terrier']

print("=" * 60)
print("PyTorch Diagnostic Script - WITH FIX")
print("=" * 60)

print(f"\n1. PyTorch version: {torch.__version__}")
print(f"2. MKL-DNN enabled: {torch.backends.mkldnn.enabled}")
print(f"3. Environment variables:")
print(f"   - MKL_THREADING_LAYER: {os.environ.get('MKL_THREADING_LAYER', 'Not set')}")
print(f"   - OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS', 'Not set')}")
print(f"   - MKL_NUM_THREADS: {os.environ.get('MKL_NUM_THREADS', 'Not set')}")

print("\n4. Loading model...")
try:
    model_ft = models.resnet18(weights='IMAGENET1K_V1')
    num_ftrs = model_ft.fc.in_features
    model_ft.fc = nn.Linear(num_ftrs, len(class_names))
    
    state_dict = torch.load('resnet18_best.pth', map_location='cpu', weights_only=False)
    model_ft.load_state_dict(state_dict)
    model_ft.eval()
    print("   ✓ Model loaded successfully")
except Exception as e:
    print(f"   ✗ Model loading failed: {e}")
    exit(1)

print("\n5. Creating dummy image...")
dummy_image = Image.new('RGB', (224, 224), color='red')

print("\n6. Testing prediction function...")
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

try:
    # Transform
    input_tensor = transform(dummy_image)
    print(f"   ✓ Transform successful. Tensor shape: {input_tensor.shape}")
    
    # Add batch dimension
    input_tensor = input_tensor.unsqueeze(0)
    print(f"   ✓ Batch dimension added. Tensor shape: {input_tensor.shape}")
    
    # Inference
    with torch.no_grad():
        outputs = model_ft(input_tensor)
        print(f"   ✓ Forward pass successful. Output shape: {outputs.shape}")
        
        probs = F.softmax(outputs, dim=1)
        print(f"   ✓ Softmax successful. Probs shape: {probs.shape}")
        
        top3_conf, top3_idx = torch.topk(probs, 3)
        print(f"   ✓ Top-3 extraction successful")
        
    # Convert to list
    top3_conf = top3_conf.squeeze().tolist()
    top3_idx = top3_idx.squeeze().tolist()
    
    results = [(class_names[idx], conf) for idx, conf in zip(top3_idx, top3_conf)]
    
    print("\n7. Prediction results (dummy red image):")
    for i, (breed, conf) in enumerate(results, 1):
        print(f"   {i}. {breed}: {conf*100:.2f}%")
    
    print("\n" + "=" * 60)
    print("✓✓✓ SUCCESS! The fix works! ✓✓✓")
    print("=" * 60)
    print("\nYou can now use main_final_fix.py for your LINE bot!")
    
except Exception as e:
    print(f"\n   ✗ Prediction failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗✗✗ FAILED! The fix didn't work. ✗✗✗")
    print("=" * 60)