# Debugging Checklist - Webhook Not Appearing on Telex

## Step 1: Check Server Logs
When you send a request from Telex, look for these log patterns:

```
[REQUEST] Received A2A request (id=...)
[REQUEST] User message: ...
[REQUEST] Webhook URL: https://ping.telex.im/...
[REQUEST] Webhook token present: True
[WEBHOOK] Starting background task
[WEBHOOK] Generating motivation from message: ...
[WEBHOOK] Generated motivation: ...
[WEBHOOK] Sending POST to: https://ping.telex.im/...
[WEBHOOK] Response status: 200
```

## Step 2: Identify Where It Breaks

### If you see logs up to `[REQUEST]` but NOT `[WEBHOOK]`:
- Problem: Background task not starting or Pydantic validation failing
- Solution: Check that request format matches A2A protocol exactly

### If you see `[WEBHOOK] Generated motivation` but NOT webhook response:
- Problem: Webhook POST is failing
- Check:
  1. Webhook URL is correct
  2. Token is present in request
  3. Network connectivity
  4. Response format is correct

### If you see webhook status != 200:
- Problem: Telex is rejecting the webhook response
- Common issues:
  - ❌ Wrong response format (missing `jsonrpc`, `id`, or `result` field)
  - ❌ Invalid JWT token in Authorization header
  - ❌ Response timeout (> 5 seconds)
  - ❌ Malformed JSON

## Step 3: Common Issues & Fixes

### Issue 1: Empty Response
**Symptom**: Webhook status 200 but response says error
**Check**: 
- Is MotivationService returning empty string?
- Is OpenRouter API responding?
- Add logging to services.py

### Issue 2: Token Issues
**Symptom**: Webhook status 401 Unauthorized
**Check**:
- Token is correctly extracted from `pushNotificationConfig.token`
- Bearer prefix is correct: `Authorization: Bearer {token}`
- Token is not None

### Issue 3: Timeout
**Symptom**: Webhook logs show timeout error
**Check**:
- OpenRouter API response time
- Network latency
- Increase timeout in main.py (currently 10 seconds)

### Issue 4: URL Mismatch
**Symptom**: No response from webhook endpoint
**Check**:
- URL format: Should start with `https://ping.telex.im/v1/a2a/webhooks/`
- URL is accessible from your server
- Telex webhook endpoint is actually listening

## Step 4: Testing Locally

Run the test script to simulate Telex behavior:

```bash
# Terminal 1
python main.py

# Terminal 2
python test_webhook.py
```

This will show you exactly what's happening in the full flow.

## Step 5: Enable Extra Debugging

Add this to `main.py` right after imports:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Show ALL logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Questions to Answer

1. Are you seeing `[REQUEST]` logs when Telex sends a request?
2. Are you seeing `[WEBHOOK]` logs after?
3. What is the `[WEBHOOK] Response status:` value?
4. What does the response body say after `Response body:`?

## Next Steps

1. Share the complete logs from sending a test request
2. We can identify exactly where the flow breaks
3. Fix accordingly
