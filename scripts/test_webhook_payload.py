#!/usr/bin/env python3
"""
Test Meta WhatsApp Cloud API Webhook Simulation Script:
- Simulates Meta verification GET challenge
- Simulates inbound employee message (Check-in, Check-out, Daily tasks)
- Demonstrates idempotent deduplication using unique `message_id`
"""

import sys
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"
VERIFY_TOKEN = "your_custom_webhook_verify_token_here"


def test_verification():
    print("\n--- 1. Testing Webhook Verification (GET) ---")
    challenge_token = "1158201444"
    url = f"{BASE_URL}/webhook?hub.mode=subscribe&hub.challenge={challenge_token}&hub.verify_token={VERIFY_TOKEN}"

    try:
        res = httpx.get(url, timeout=5.0)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        assert res.status_code == 200 and res.text == challenge_token
        print("Webhook Verification test passed.")
    except Exception as e:
        print(f"Failed to connect or verify: {e}")


def test_inbound_message():
    print("\n--- 2. Testing Inbound WhatsApp Message (POST) ---")
    message_id = f"wamid.HBgL{uuid.uuid4().hex[:16]}"
    phone = "94771234567"  # Meta sends phone without plus in payload from field

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "100000000000000",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "15551234567", "phone_number_id": "100000000000000"},
                            "contacts": [{"wa_id": phone, "profile": {"name": "Kasun Perera"}}],
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": phone,
                                    "timestamp": "1728543600",
                                    "type": "text",
                                    "text": {
                                        "body": "Checking out for today. Worked on 2 tasks:\n1. Fixed auth token expiry bug (2 hours)\n2. Created database migration script (1 hour)"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    try:
        # First send: Should be processed
        res1 = httpx.post(f"{BASE_URL}/webhook", json=payload, timeout=10.0)
        print(f"First attempt Status: {res1.status_code}")
        print(f"First attempt Result: {res1.json()}")

        # Second send with same message_id: Should trigger idempotency and return duplicate_ignored
        print("\n--- 3. Testing Idempotency (Sending Same Message ID Again) ---")
        res2 = httpx.post(f"{BASE_URL}/webhook", json=payload, timeout=10.0)
        print(f"Second attempt Status: {res2.status_code}")
        print(f"Second attempt Result: {res2.json()}")
        print("Idempotency test completed.")
    except Exception as e:
        print(f"Failed to send webhook message: {e}")


if __name__ == "__main__":
    test_verification()
    test_inbound_message()
