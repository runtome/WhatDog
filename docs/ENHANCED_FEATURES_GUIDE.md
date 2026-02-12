# Enhanced Features Guide

## New Features

### 1. 🧠 Thinking Process Filtering
The bot now handles `<think>...</think>` tags in Thai LLM responses:
- **In Logs**: Full response WITH `<think>` tags is saved
- **To User**: Response WITHOUT `<think>` tags is sent

### 2. 🐶 Automatic Dog Breed Information
After detecting a dog breed from an image, the bot automatically:
1. Shows top 3 breed predictions
2. Asks Thai LLM for detailed information about the #1 breed
3. Gets comparison between all 3 predicted breeds
4. Sends everything in one message

## How It Works

### Text Message with Thinking Process

**User sends:** "อธิบายเกี่ยวกับสุนัข"

**Thai LLM responds:**
```
<think>
ผู้ใช้ต้องการข้อมูลเกี่ยวกับสุนัข ควรอธิบายแบบกว้างๆ
พูดถึงประเภท นิสัย และการดูแล
</think>
สุนัขเป็นสัตว์เลี้ยงที่ภักดี มีหลายสายพันธุ์...
```

**User sees:**
```
สุนัขเป็นสัตว์เลี้ยงที่ภักดี มีหลายสายพันธุ์...
```

**Log file contains:**
```csv
time,line_user,question,answer_reply,thinking_process,response_time
14:30:45,U123...,อธิบายเกี่ยวกับสุนัข,สุนัขเป็นสัตว์เลี้ยง...,ผู้ใช้ต้องการข้อมูลเกี่ยวกับสุนัข...,1.234s
```

### Image with Automatic Breed Info

**User uploads dog image**

**Bot responds with:**
```
🐶 สายพันธ์น้องหมา
📊 มีความน่าจะเป็นดังนี้:
1. Chihuahua (95.23%)
2. Mexican hairless (3.45%)
3. toy terrier (1.32%)

📖 ข้อมูลเพิ่มเติม:
ข้อมูลเกี่ยวกับสายพันธุ์ Chihuahua:
- ลักษณะเด่น: เป็นสุนัขขนาดเล็กที่สุดในโลก มีน้ำหนักเพียง 1-3 กิโลกรัม
- นิสัย: ร่าเริง กล้าหาญ รักเจ้าของมาก
- ขนาดตัว: สูง 15-23 ซม.
- การดูแล: ต้องการการดูแลพิเศษในเรื่องอุณหภูมิ

เปรียบเทียบความแตกต่างระหว่าง 3 สายพันธุ์:
- Chihuahua: เล็กที่สุด มีขนสั้นหรือยาว
- Mexican hairless: ไม่มีขน ผิวเรียบ ต้องทาครีม
- Toy terrier: มีขนสั้น ตัวเล็กคล้าย Chihuahua แต่หูตั้งตรง
```

## Configuration

### Customize LLM Parameters

In `main_enhanced.py`, you can adjust:

```python
# For text messages
ask_thai_llm(text, max_tokens=2048, temperature=0.3)

# For dog breed info
ask_thai_llm(prompt, max_tokens=1500, temperature=0.3)
```

**Adjust max_tokens for breed info:**
```python
# In get_dog_breed_info() function
breed_info, thinking = ask_thai_llm(prompt, max_tokens=1500, temperature=0.3)
#                                              ^^^^ Change this

# 500 = Very brief
# 1000 = Brief
# 1500 = Detailed (default)
# 2000 = Very detailed
```

### Customize Breed Info Prompt

Edit the prompt in `get_dog_breed_info()`:

```python
prompt = f"""ผลการทำนายสายพันธุ์สุนัข:
1. {formatted_breeds[0][0]} ({formatted_breeds[0][1]*100:.1f}%)
2. {formatted_breeds[1][0]} ({formatted_breeds[1][1]*100:.1f}%)
3. {formatted_breeds[2][0]} ({formatted_breeds[2][1]*100:.1f}%)

กรุณาให้ข้อมูลดังนี้:

1. ข้อมูลเกี่ยวกับสายพันธุ์ {formatted_breeds[0][0]}:
   - ลักษณะเด่น
   - นิสัย
   - ขนาดตัว
   - การดูแล

2. เปรียบเทียบความแตกต่างระหว่าง 3 สายพันธุ์

ตอบเป็นภาษาไทยแบบกระชับ ไม่เกิน 500 คำ"""
```

**Examples of custom prompts:**

**Short version (faster):**
```python
prompt = f"""สายพันธุ์สุนัข: {formatted_breeds[0][0]}

บอกข้อมูลสั้นๆ:
- ลักษณะ
- นิสัย
- การดูแล

ตอบไม่เกิน 200 คำ"""
```

**Detailed version (slower):**
```python
prompt = f"""ผลการทำนาย:
1. {formatted_breeds[0][0]} ({formatted_breeds[0][1]*100:.1f}%)
2. {formatted_breeds[1][0]} ({formatted_breeds[1][1]*100:.1f}%)
3. {formatted_breeds[2][0]} ({formatted_breeds[2][1]*100:.1f}%)

ให้ข้อมูลครบถ้วน:
- ประวัติความเป็นมา
- ลักษณะทางกายภาพ
- นิสัยและอารมณ์
- การดูแลเฉพาะ
- โรคที่พบบ่อย
- ข้อดี-ข้อเสีย
- เหมาะกับใคร

เปรียบเทียบทั้ง 3 สายพันธุ์โดยละเอียด"""
```

## Viewing Logs with Thinking Process

### Basic View (No Thinking)
```bash
python view_logs_enhanced.py
```

### View with Thinking Process
```bash
python view_logs_enhanced.py --show-thinking
# or
python view_logs_enhanced.py -t
```

### View Specific Date
```bash
python view_logs_enhanced.py 05-02-2026 --show-thinking
```

### Search Logs
```bash
# Search for specific term
python view_logs_enhanced.py --search "Chihuahua"

# Search in specific date
python view_logs_enhanced.py --search "Chihuahua" 05-02-2026
```

## Log File Format

The new CSV format includes `thinking_process` column:

```csv
time,line_user,question,answer_reply,thinking_process,response_time
14:30:45,U123...,สวัสดี,สวัสดีครับ,ผู้ใช้ทักทาย...,0.234s
14:31:20,U123...,[IMAGE] file.jpg,🐶 สายพันธุ์...,วิเคราะห์ว่าเป็น...,3.456s
```

## Examples

### Example 1: Text with Thinking

**User:** "ทำไมสุนัขถึงชอบเห่า"

**Thai LLM Internal:**
```
<think>
คำถามเกี่ยวกับพฤติกรรมสุนัข
ควรอธิบายสาเหตุหลายประการ
ใช้ภาษาเข้าใจง่าย
</think>
สุนัขเห่าเพื่อสื่อสารหลายเหตุผล:
1. เตือนภัย
2. ขอความสนใจ
3. แสดงความตื่นเต้น
...
```

**User sees:**
```
สุนัขเห่าเพื่อสื่อสารหลายเหตุผล:
1. เตือนภัย
2. ขอความสนใจ
3. แสดงความตื่นเต้น
...
```

**Log contains both!**

### Example 2: Image Analysis

**User uploads Golden Retriever image**

**Step 1: Model predicts**
```
1. golden_retriever (92.34%)
2. Labrador_retriever (5.23%)
3. flat-coated_retriever (1.45%)
```

**Step 2: Bot asks LLM**
```
Prompt: "ผลการทำนาย:
1. golden retriever (92.3%)
2. Labrador retriever (5.2%)
3. flat-coated retriever (1.5%)

ให้ข้อมูลเกี่ยวกับ golden retriever และเปรียบเทียบ..."
```

**Step 3: LLM responds (with thinking)**
```
<think>
ควรเน้นลักษณะเด่นของ Golden
อธิบายความต่างกับ Labrador
กล่าวถึง flat-coated แบบสั้นๆ
</think>
Golden Retriever เป็นสุนัขขนาดใหญ่พันธุ์ยอดนิยม...
[ข้อมูลละเอียด]

เปรียบเทียบ:
- Golden: ขนยาว สีทอง นิสัยอ่อนโยน
- Labrador: ขนสั้น หลายสี กระฉับกระเฉง
- Flat-coated: ขนยาว สีดำหรือน้ำตาล คล้าย Golden
```

**Step 4: User sees**
```
🐶 สายพันธ์น้องหมา
📊 มีความน่าจะเป็นดังนี้:
1. golden retriever (92.34%)
2. Labrador retriever (5.23%)
3. flat-coated retriever (1.45%)

📖 ข้อมูลเพิ่มเติม:
Golden Retriever เป็นสุนัขขนาดใหญ่พันธุ์ยอดนิยม...
[ข้อมูลโดยไม่มี <think> tags]
```

## Troubleshooting

### Issue: Thinking tags appearing in user messages

**Check:**
```python
# In handle_text_message()
thinking_content = ''

full_response, thinking, clean_response = ask_thai_llm(text)

if clean_response:
    reply_text = clean_response  # ✅ Using clean_response (no tags)
    thinking_content = thinking or ''
```

Make sure you're using `clean_response` not `full_response`!

### Issue: Dog breed info too long

**Solution:** Reduce max_tokens
```python
# In get_dog_breed_info()
breed_info, thinking = ask_thai_llm(prompt, max_tokens=800, temperature=0.3)
#                                              ^^^ Reduced from 1500
```

### Issue: Dog breed info too slow

**Solution 1:** Disable breed info temporarily
```python
# Comment out this section in handle_image_message()
# breed_info, thinking_content = get_dog_breed_info(top3_predictions[0][0], top3_predictions)
# 
# if breed_info:
#     full_reply = f"{initial_reply}\n\n📖 ข้อมูลเพิ่มเติม:\n{breed_info}"
# else:
#     full_reply = initial_reply

# Just use initial_reply
full_reply = initial_reply
```

**Solution 2:** Make it shorter
```python
breed_info, thinking = ask_thai_llm(prompt, max_tokens=500, temperature=0.3)
```

### Issue: Thinking process not in logs

**Check CSV file format:**
```bash
head -1 logs/05-02-2026.csv
```

Should show:
```
time,line_user,question,answer_reply,thinking_process,response_time
```

If old format (without `thinking_process`), the file was created before update.
New conversations will have the column.

## Performance Impact

### Response Times

| Scenario | Before | After | Difference |
|----------|--------|-------|------------|
| Text message | 1-2s | 1-2s | No change |
| Image (prediction only) | 0.5-1s | N/A | - |
| Image (with breed info) | N/A | 2-5s | +1-4s |

The additional time for images is due to:
1. Model prediction: ~0.5s
2. LLM API call for breed info: ~1-4s

### Optimization Options

**Option 1: Cache common breeds**
```python
breed_cache = {}

def get_dog_breed_info_cached(breed_name, top3_breeds):
    cache_key = f"{breed_name}_{top3_breeds[1][0]}_{top3_breeds[2][0]}"
    
    if cache_key in breed_cache:
        return breed_cache[cache_key], ''
    
    info, thinking = get_dog_breed_info(breed_name, top3_breeds)
    breed_cache[cache_key] = info
    return info, thinking
```

**Option 2: Async processing (advanced)**
Send prediction first, then breed info as second message.

## Migration from Old Version

### Update Process

1. **Backup current file:**
   ```bash
   cp main.py main_backup.py
   ```

2. **Use new version:**
   ```bash
   cp main_enhanced.py main.py
   ```

3. **Restart bot:**
   ```bash
   # Stop current bot (Ctrl+C)
   waitress-serve --listen=0.0.0.0:5000 main:app
   ```

### Log File Compatibility

- **Old logs** (without `thinking_process`): Still work, column will be empty
- **New logs**: Include `thinking_process` column
- **Viewer**: Works with both old and new formats

---

🎉 Your bot now has enhanced thinking process logging and automatic dog breed information!
