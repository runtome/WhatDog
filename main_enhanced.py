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
import requests
import json
import csv
import time
import re

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

# Thai LLM API configuration
thai_llm_url = os.getenv("THAI_LLM_URL", "http://thaillm.or.th/api/pathumma/v1/chat/completions")
thai_llm_api_key = os.getenv("THAI_LLM_API_KEY", "----------")
thai_llm_model = os.getenv("THAI_LLM_MODEL", "/model")

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
print("Loading dog breed model...")
model_ft = models.resnet18(weights='IMAGENET1K_V1')
num_ftrs = model_ft.fc.in_features
model_ft.fc = nn.Linear(num_ftrs, len(class_names))

state_dict = torch.load('resnet18_best.pth', map_location='cpu', weights_only=False)
model_ft.load_state_dict(state_dict)
model_ft.eval()
print("Dog breed model loaded successfully!")

# Define preprocessing transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")


def extract_think_tags(text):
    """
    Extract <think>...</think> content and return both the thinking process and clean text.
    
    Returns:
        tuple: (thinking_content, clean_text)
    """
    # Find all <think>...</think> blocks
    think_pattern = r'<think>(.*?)</think>'
    think_matches = re.findall(think_pattern, text, re.DOTALL)
    
    # Join all thinking content
    thinking_content = '\n'.join(think_matches) if think_matches else ''
    
    # Remove <think>...</think> blocks from text
    clean_text = re.sub(think_pattern, '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()
    
    return thinking_content, clean_text


def log_conversation(user_id, question, answer, response_time, thinking_content=''):
    """
    Log conversation to CSV file with format: DD-MM-YYYY.csv
    Creates new file if it doesn't exist or if it's a new day
    Now includes thinking_content column
    """
    # Get current date and time
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")
    
    # Create filename based on date
    csv_filename = os.path.join("logs", f"{date_str}.csv")
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_filename)
    
    # Write to CSV
    try:
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['time', 'line_user', 'question', 'answer_reply', 'thinking_process', 'response_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the log entry
            writer.writerow({
                'time': time_str,
                'line_user': user_id,
                'question': question,
                'answer_reply': answer,
                'thinking_process': thinking_content,
                'response_time': f"{response_time:.3f}s"
            })
            
        print(f"Logged to {csv_filename}: {user_id} - {question[:30]}...")
    except Exception as e:
        print(f"Error logging to CSV: {e}")


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


def ask_thai_llm(user_message, max_tokens=2048, temperature=0.3):
    """
    Ask Thai LLM API a question
    
    Args:
        user_message: User's question/message
        max_tokens: Maximum tokens in response (default: 2048)
        temperature: Response creativity 0.0-1.0 (default: 0.3)
    
    Returns:
        tuple: (full_response_with_think, thinking_content, clean_response) or (None, None, None) if error
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": thai_llm_api_key
        }
        
        payload = {
            "model": thai_llm_model,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        print(f"Calling Thai LLM API for: {user_message[:50]}...")
        
        response = requests.post(
            thai_llm_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract response from the API result
            if 'choices' in result and len(result['choices']) > 0:
                full_message = result['choices'][0]['message']['content']
                
                # Extract thinking and clean text
                thinking_content, clean_text = extract_think_tags(full_message)
                
                print(f"Thai LLM response received: {clean_text[:50]}...")
                if thinking_content:
                    print(f"Thinking process captured: {thinking_content[:50]}...")
                
                return full_message, thinking_content, clean_text
            else:
                print(f"Unexpected API response structure: {result}")
                return None, None, None
        else:
            print(f"Thai LLM API error: {response.status_code} - {response.text}")
            return None, None, None
            
    except requests.exceptions.Timeout:
        print("Thai LLM API timeout")
        return None, None, None
    except Exception as e:
        print(f"Thai LLM error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def get_dog_breed_info(breed_name, top3_breeds):
    """
    Ask Thai LLM for detailed information about the top breed and comparison with other breeds.
    
    Args:
        breed_name: The top predicted breed name
        top3_breeds: List of tuples [(breed1, conf1), (breed2, conf2), (breed3, conf3)]
    
    Returns:
        str: LLM response about the breed
    """
    # Format breed names nicely (replace underscores with spaces)
    formatted_breeds = [(name.replace('_', ' '), conf) for name, conf in top3_breeds]
    
    # Create prompt for LLM
    prompt = f"""ผลการทำนายสายพันธุ์สุนัข:
1. {formatted_breeds[0][0]} ({formatted_breeds[0][1]*100:.1f}%)
2. {formatted_breeds[1][0]} ({formatted_breeds[1][1]*100:.1f}%)
3. {formatted_breeds[2][0]} ({formatted_breeds[2][1]*100:.1f}%)

กรุณาให้ข้อมูลดังนี้:

1. ข้อมูลเกี่ยวกับสายพันธุ์ {formatted_breeds[0][0]} (สายพันธุ์ที่มีความน่าจะเป็นสูงสุด):
   - ลักษณะเด่น
   - นิสัย
   - ขนาดตัว
   - การดูแล

2. เปรียบเทียบความแตกต่างระหว่าง 3 สายพันธุ์นี้:
   - {formatted_breeds[0][0]}
   - {formatted_breeds[1][0]}
   - {formatted_breeds[2][0]}

ตอบเป็นภาษาไทยแบบกระชับและเข้าใจง่าย ไม่เกิน 500 คำ"""

    # Call Thai LLM
    full_response, thinking, clean_response = ask_thai_llm(prompt, max_tokens=1500, temperature=0.3)
    
    if clean_response:
        return clean_response, thinking
    else:
        return None, None


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
    start_time = time.time()
    
    text = event.message.text
    user_id = event.source.user_id
    
    print(f"Received text from {user_id}: {text}")

    # Predefined responses (optional - for quick replies)
    quick_responses = {
        "สวัสดี": "สวัสดีครับ ยินดีที่ได้รู้จักนะครับ 😊",
        "ชื่ออะไร": "ผมชื่อไลน์บอทครับ สามารถส่งรูปน้องหมามาให้ผมทายสายพันธุ์ได้เลยครับ 🐶",
    }

    thinking_content = ''
    
    # Check if there's a quick response
    if text in quick_responses:
        reply_text = quick_responses[text]
    else:
        # Use Thai LLM API for general chat
        full_response, thinking, clean_response = ask_thai_llm(text)
        
        if clean_response:
            reply_text = clean_response
            thinking_content = thinking or ''
        else:
            # Fallback if LLM is not available
            reply_text = "ขอโทษครับ ขณะนี้ระบบตอบคำถามไม่สามารถใช้งานได้ 🙏\n\nคุณสามารถส่งรูปน้องหมามาให้ผมทายสายพันธุ์ได้เลยครับ 🐶"
    
    # Send reply (without <think> tags)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Log conversation (with thinking process)
    log_conversation(user_id, text, reply_text, response_time, thinking_content)

# Handle image messages
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    start_time = time.time()
    
    message_id = event.message.id
    user_id = event.source.user_id

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
        
        # Format the prediction results
        prediction_text = "\n".join(
            [f"{i+1}. {class_name.replace('_', ' ')} ({confidence*100:.2f}%)" 
             for i, (class_name, confidence) in enumerate(top3_predictions)]
        )
        
        # Initial reply with predictions
        initial_reply = f"🐶 สายพันธ์น้องหมา\n📊 มีความน่าจะเป็นดังนี้:\n{prediction_text}"
        
        print(f"Prediction results:\n{prediction_text}")
        
        # Get detailed information from LLM about the breeds
        print("Getting breed information from Thai LLM...")
        breed_info, thinking_content = get_dog_breed_info(top3_predictions[0][0], top3_predictions)
        
        # Combine prediction and breed info
        if breed_info:
            full_reply = f"{initial_reply}\n\n📖 ข้อมูลเพิ่มเติม:\n{breed_info}"
        else:
            full_reply = initial_reply
        
        # Reply to the user
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text=full_reply)
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log conversation (with thinking process if available)
        log_conversation(
            user_id, 
            f"[IMAGE] {image_filename}", 
            full_reply, 
            response_time,
            thinking_content or ''
        )
        
    except Exception as e:
        print(f"Error in handle_image_message: {e}")
        import traceback
        traceback.print_exc()
        
        error_message = "ขอโทษครับ เกิดข้อผิดพลาดในการทำนาย กรุณาลองใหม่อีกครั้ง"
        
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_message)
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log error
            log_conversation(user_id, "[IMAGE] Error", error_message, response_time)
        except:
            pass

if __name__ == "__main__":
    # For development only
    app.run(debug=False, host='0.0.0.0', port=5000)
