#!/usr/bin/env python3
"""
Test script for Thai LLM API
Tests the connection and response from thaillm.or.th
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Thai LLM API configuration
THAI_LLM_URL = os.getenv("THAI_LLM_URL", "http://thaillm.or.th/api/pathumma/v1/chat/completions")
THAI_LLM_API_KEY = os.getenv("THAI_LLM_API_KEY", "Your API KEY")
THAI_LLM_MODEL = os.getenv("THAI_LLM_MODEL", "/model")


def test_thai_llm(message, max_tokens=2048, temperature=0.3):
    """Test Thai LLM API with a message."""
    
    print("=" * 80)
    print("Testing Thai LLM API")
    print("=" * 80)
    print(f"URL: {THAI_LLM_URL}")
    print(f"API Key: {THAI_LLM_API_KEY[:10]}...{THAI_LLM_API_KEY[-5:]}")
    print(f"Model: {THAI_LLM_MODEL}")
    print(f"Message: {message}")
    print("=" * 80)
    
    headers = {
        "Content-Type": "application/json",
        "apikey": THAI_LLM_API_KEY
    }
    
    payload = {
        "model": THAI_LLM_MODEL,
        "messages": [
            {"role": "user", "content": message}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    print("\n📤 Sending request...")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            THAI_LLM_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📥 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print("\nFull Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Extract the actual message
            if 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0]['message']['content']
                print("\n" + "=" * 80)
                print("🤖 Thai LLM Response:")
                print("=" * 80)
                print(message_content)
                print("=" * 80)
                return message_content
            else:
                print("\n⚠️ Unexpected response structure")
                return None
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (30 seconds)")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_tests():
    """Run multiple test cases."""
    
    test_cases = [
        "สวัสดี",
        "คุณชื่ออะไร",
        "บอกเกี่ยวกับสุนัข 3 สายพันธุ์ที่นิยม",
        "อธิบายความแตกต่างระหว่างสุนัขพันธุ์ชิวาวากับพุดเดิ้ล",
    ]
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║            Thai LLM API Test Suite                           ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"Test Case {i}/{len(test_cases)}")
        print(f"{'#'*80}\n")
        
        result = test_thai_llm(test_message)
        
        if result:
            print(f"\n✅ Test {i} passed")
        else:
            print(f"\n❌ Test {i} failed")
        
        # Wait a bit between requests
        if i < len(test_cases):
            import time
            print("\nWaiting 2 seconds before next test...")
            time.sleep(2)
    
    print("\n\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with custom message
        message = " ".join(sys.argv[1:])
        test_thai_llm(message)
    else:
        # Run all test cases
        run_tests()
