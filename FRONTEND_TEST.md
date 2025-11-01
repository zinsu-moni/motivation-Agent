# Frontend Testing Guide

## Quick Start

1. **Make sure your server is running:**
   ```bash
   python main.py
   ```
   You should see: `Uvicorn running on http://127.0.0.1:8000`

2. **Open the frontend:**
   - Open your browser and go to: `http://localhost:8000`
   - You should see the "Motivo AI — Test UI" page

3. **Send a test request:**
   - The message field is pre-filled with a sample message
   - Click the **📤 Send Request** button
   - The response will appear in the "Response" section below

## What You'll See

### Successful Response (Blocking Mode)
```json
{
  "jsonrpc": "2.0",
  "id": "test-abc123def",
  "result": {
    "message": {
      "parts": [
        {
          "type": "text",
          "text": "You've got this! The home stretch is where champions are made..."
        }
      ],
      "messageId": "msg-12345"
    }
  }
}
```

### Async Response (Webhook Mode)
If your request includes webhook configuration:
```json
{
  "jsonrpc": "2.0",
  "id": "test-abc123def",
  "result": null
}
```

Response is delivered via webhook in the background.

## Testing Different Scenarios

### Test 1: Simple Motivation Request
**Message:** "I need a quick motivational boost to finish my project."

**Expected:** Get a motivational response within 5-10 seconds

### Test 2: Different Topic
**Message:** "Help me stay focused during a long meeting"

**Expected:** Response adapted to the new scenario

### Test 3: Very Short Message
**Message:** "Help!"

**Expected:** Response works even with minimal input

## Troubleshooting

### ❌ "Network error: fetch failed"
- Make sure the server is running on port 8000
- Check firewall settings

### ❌ "Error 404"
- Frontend file wasn't found
- Make sure `static/` folder exists with `index.html`

### ❌ "No response after 30 seconds"
- The API call may have timed out
- Check server logs for `[SERVICE]` messages

### ✅ "Error 422"
- Request format is invalid
- Check the JSON-RPC 2.0 format in browser console (right-click → Inspect → Console)

## Browser Developer Tools

To see the actual request and response:

1. Press `F12` to open Developer Tools
2. Go to the **Console** tab
3. Send a request through the frontend
4. You'll see: `Sending A2A request:` followed by the JSON request body
5. In the **Network** tab, you can see the full request/response details

## Next Steps

- ✅ Verify API endpoint works
- ✅ Test motivation generation
- ✅ Check response formatting
- Then test with your Telex agent using the same request format

