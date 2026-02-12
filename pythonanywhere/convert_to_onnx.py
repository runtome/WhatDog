"""
Convert PyTorch ResNet18 model to ONNX format
Run this LOCALLY (on your computer with PyTorch installed) before deploying to PythonAnywhere

This creates a much smaller model file that can run without PyTorch
"""

import torch
import torchvision.models as models
import torch.nn as nn

# Define class names (same as in your original code)
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

print("=" * 80)
print("PyTorch to ONNX Model Converter")
print("=" * 80)

# Load the PyTorch model
print("\n1. Loading PyTorch model...")
model_ft = models.resnet18(weights='IMAGENET1K_V1')
num_ftrs = model_ft.fc.in_features
model_ft.fc = nn.Linear(num_ftrs, len(class_names))

# Load your trained weights
print("2. Loading trained weights from resnet18_best.pth...")
state_dict = torch.load('resnet18_best.pth', map_location='cpu', weights_only=False)
model_ft.load_state_dict(state_dict)
model_ft.eval()

print("3. Creating dummy input (1, 3, 224, 224)...")
dummy_input = torch.randn(1, 3, 224, 224)

# Export to ONNX
print("4. Converting to ONNX format...")
output_path = "dog_breed_model.onnx"

torch.onnx.export(
    model_ft,                           # Model
    dummy_input,                        # Model input
    output_path,                        # Output file
    export_params=True,                 # Store trained weights
    opset_version=11,                   # ONNX version
    do_constant_folding=True,           # Optimize constants
    input_names=['input'],              # Input tensor name
    output_names=['output'],            # Output tensor name
    dynamic_axes={
        'input': {0: 'batch_size'},     # Variable batch size
        'output': {0: 'batch_size'}
    }
)

print(f"\n✅ SUCCESS! Model exported to: {output_path}")

# Check file size
import os
original_size = os.path.getsize('resnet18_best.pth')
onnx_size = os.path.getsize(output_path)

print(f"\n📊 File Sizes:")
print(f"   Original PyTorch (.pth): {original_size / 1024 / 1024:.2f} MB")
print(f"   ONNX (.onnx): {onnx_size / 1024 / 1024:.2f} MB")
print(f"   Difference: {(original_size - onnx_size) / 1024 / 1024:.2f} MB")

# Test the ONNX model
print(f"\n5. Testing ONNX model...")
import onnxruntime as ort

session = ort.InferenceSession(output_path)

# Run inference
outputs = session.run(
    None,
    {'input': dummy_input.numpy()}
)

print(f"   ✅ ONNX model works!")
print(f"   Output shape: {outputs[0].shape}")

# Test with actual predictions
import numpy as np
probs = np.exp(outputs[0]) / np.sum(np.exp(outputs[0]), axis=1, keepdims=True)
top3_idx = np.argsort(probs[0])[::-1][:3]
top3_conf = probs[0][top3_idx]

print(f"\n6. Test predictions (random input):")
for i, (idx, conf) in enumerate(zip(top3_idx, top3_conf), 1):
    print(f"   {i}. {class_names[idx]}: {conf*100:.2f}%")

print("\n" + "=" * 80)
print("✅ Conversion complete!")
print("=" * 80)
print("\nNext steps:")
print("1. Upload 'dog_breed_model.onnx' to PythonAnywhere")
print("2. Use 'main_pythonanywhere.py' instead of the PyTorch version")
print("3. Install only: pip install onnxruntime pillow --user")
print("=" * 80)
