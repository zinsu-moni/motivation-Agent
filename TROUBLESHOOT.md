# Response Not Appearing on Telex - Troubleshooting Guide

## Status
✅ Your agent is working up to the webhook POST
❌ Responses aren't appearing on Telex agent dashboard

## Root Causes (Most to Least Likely)

### 1. **Webhook Response Format Issue** (Most Likely)
The response might have the wrong structure. Even if Telex returns 200, it might not display because:
- Missing required fields
- Wrong field names or structure
- Response not matching A2A specification

**What we sent:**
```json
{
  "jsonrpc": "2.0",
  "id": "same-as-request",
  "result": {
    "message": {
      "kind": "message",
      "role": "assistant",
      "parts": [
        {"kind": "text", "text": "motivation here"}
      ]
    }
  }
}
```

**What Telex might expect** (variation):
```json
{
  "jsonrpc": "2.0",
  "id": "same-as-request",
  "result": {
    "message": {
      "kind": "message",
      "role": "assistant",
      "parts": [
        {"kind": "text", "text": "motivation here"}
      ],
      "messageId": "unique-id"  // <- Might be required
    }
  }
}
```

---

### 2. **Webhook Not Being Sent at All**
The background task might be failing silently.

**Indicators:**
- No `[WEBHOOK] Starting background task` in logs
- No `[WEBHOOK] Sending POST to:` log
- HTTP 200 response returned, but nothing else happens

**Why it fails:**
- Pydantic validation error in webhook function
- asyncio.create_task() not executing
- Webhook config parsing issue

---

### 3. **Webhook POST is Failing Silently**
The POST request is failing but not logging properly.

**Indicators:**
- Logs show task started
- Logs show motivation generated
- But NO logs for "Sending POST" or webhook response

---

### 4. **Token Authentication Issue**
The JWT token from Telex isn't being used correctly.

**Common problems:**
- ❌ Token is `None` (not extracted from request)
- ❌ Wrong Authorization header format
- ❌ Token expired or invalid

---

## What We Need to Know

### Run this immediately:

1. **Start your server:**
   ```bash
   python main.py
   ```

2. **Send a test request from Telex**

3. **Share ALL the logs** starting from "Received A2A request"

Specifically, we need to see:
- `[REQUEST]` logs
- `[WEBHOOK]` logs
- Any error messages

### The logs will tell us:
- Where the flow breaks
- What the webhook response was
- Why Telex didn't display it

---

## Immediate Fix Attempts

### Option A: Add `messageId` to Response
This might be required by Telex:

In `main.py`, modify the webhook response building:

```python
# Before:
result = {
    "message": {
        "kind": "message",
        "role": "assistant",
        "parts": [...]
    }
}

# After:
result = {
    "message": {
        "kind": "message",
        "role": "assistant",
        "parts": [...],
        "messageId": f"response-{request_id}"  # Add this
    }
}
```

### Option B: Check API Response Handling
Make sure OpenRouter is actually responding:

In `services.py`, add to `generate_motivation()`:

```python
logger.info(f"Response type: {type(response)}")
logger.info(f"Choices: {response.choices}")
```

---

## Next Actions

1. **Add detailed logging** (already done in updated `main.py`)
2. **Send test request from Telex**
3. **Share complete logs**
4. **We identify the exact failure point**
5. **Apply targeted fix**

---

## If You Want to Test Locally First

```bash
# Terminal 1
python main.py

# Terminal 2
python test_webhook.py
```

This simulates Telex behavior and won't depend on Telex infrastructure.

---

## Questions?

When you're ready, provide:
1. The complete logs after sending a message to the agent
2. Any errors or warnings in the console
3. What you see (or don't see) on the Telex agent page
