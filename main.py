from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
import os
import datetime
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision import models
import torch.nn as nn
import torch.nn.functional as F
from dotenv import load_dotenv
from io import BytesIO

# ============================================================
# CRITICAL FIX: Must be set BEFORE importing torch operations
# ============================================================
os.environ['MKL_THREADING_LAYER'] = 'GNU'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

# Disable MKL-DNN to avoid "could not create a primitive" error
torch.backends.mkldnn.enabled = False

load_dotenv()


# Get environment variables
channel_secret = os.getenv("CHANNEL_SECRET")
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")

if not channel_secret or not channel_access_token:
    raise ValueError("Missing CHANNEL_SECRET or CHANNEL_ACCESS_TOKEN environment variables.")

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Define class names for the prediction
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

# Load the trained model
print("Loading model...")
model_ft = models.resnet18(weights='IMAGENET1K_V1')
num_ftrs = model_ft.fc.in_features
model_ft.fc = nn.Linear(num_ftrs, len(class_names))

state_dict = torch.load('resnet18_best.pth', map_location='cpu', weights_only=False)
model_ft.load_state_dict(state_dict)
model_ft.eval()
print("Model loaded successfully!")

# Define preprocessing transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def predict_pil(image):
    """Predict dog breed from PIL image."""
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Transform image and add batch dimension
    input_tensor = transform(image).unsqueeze(0)
    
    # Make prediction
    with torch.no_grad():
        outputs = model_ft(input_tensor)
        probs = F.softmax(outputs, dim=1)
        top3_conf, top3_idx = torch.topk(probs, 3)

    # Convert to Python lists
    top3_conf = top3_conf.squeeze().tolist()
    top3_idx = top3_idx.squeeze().tolist()
    
    # Handle case where only one prediction is made
    if not isinstance(top3_conf, list):
        top3_conf = [top3_conf]
        top3_idx = [top3_idx]
    
    # Return results
    return [
        (class_names[idx], conf)
        for idx, conf in zip(top3_idx, top3_conf)
    ]


app = Flask(__name__)

# Ensure "images" folder exists
if not os.path.exists("images"):
    os.makedirs("images")

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
    
    return "Hello Line Chatbot"

# Handle text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    print(f"Received text: {text}")

    responses = {
        "สวัสดี": "สวัสดีครับ ยินดีต้อนรับสู่บริการทำนายสายพันธุ์น้องหมาครับ ส่งรูปน้องหมามาให้ผมทายสายพันธุ์ได้เลยครับ",
        "ชื่ออะไร": "ผมชื่อไลน์บอทครับ สามารถส่งรูปน้องหมามาให้ผมทายสายพันธุ์ได้เลยครับ",
    }

    reply_text = responses.get(text, "ส่งรูปเพื่อ ทำนาย 🐶 สายพันธ์น้องหมา มาได้เลยครับ")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# Handle image messages
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_id = event.message.id

    # Get current time in the format YYYY_MM_DD_HH_MM_SS
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # Construct the image filename with timestamp and message_id
    image_filename = f"{timestamp}_{message_id}.jpg"
    image_path = os.path.join("images", image_filename)

    try:
        # Download image from LINE server
        message_content = line_bot_api.get_message_content(message_id)
        
        image_bytes = BytesIO()

        # Save to both disk and memory
        with open(image_path, "wb") as img_file:
            for chunk in message_content.iter_content(chunk_size=1024):
                img_file.write(chunk)      # save to disk
                image_bytes.write(chunk)   # keep in memory

        image_bytes.seek(0)
        print(f"Image saved at: {image_path}")

        # Load image from memory
        image = Image.open(image_bytes).convert("RGB")
        
        # Predict top 3 classes and confidence scores
        top3_predictions = predict_pil(image)
        
        print(f"Top 3 Predictions: {top3_predictions}")
        
        # Format the reply
        reply_text = "\n".join(
            [f"{i+1}. {class_name} ({confidence*100:.2f}%)" 
             for i, (class_name, confidence) in enumerate(top3_predictions)]
        )
        print(f"Prediction results:\n{reply_text}")
        
        # Reply to the user
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text=f"🐶 สายพันธ์น้องหมา\n📊มีความน่าจะเป็นดังนี้:\n{reply_text}")
        )
        
    except Exception as e:
        print(f"Error in handle_image_message: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="ขอโทษครับ เกิดข้อผิดพลาดในการทำนาย กรุณาลองใหม่อีกครั้ง")
            )
        except:
            pass

if __name__ == "__main__":
    # For development only
    app.run(debug=False, host='0.0.0.0', port=5000)