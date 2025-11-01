# API Key Update Required

## Issue
Your OpenRouter API key has expired or become invalid.
- Error: `User not found` (401 Unauthorized)
- This is why requests are hanging - authentication fails

## Solution: Get a New API Key

### Step 1: Go to OpenRouter
1. Open https://openrouter.ai in your browser
2. Sign in to your account (create one if needed - it's free)

### Step 2: Generate API Key
1. Go to your account page: https://openrouter.ai/account/api-keys
2. Click **"Create New Key"** (or **"Generate"**)
3. Copy the full API key (starts with `sk-or-v1-...`)

### Step 3: Update Your .env File
1. Open `.env` in your project folder
2. Find the line: `OPENAI_API_KEY=...`
3. Replace it with your new key:
   ```
   OPENAI_API_KEY=sk-or-v1-YOUR_NEW_KEY_HERE
   ```
4. Save the file

### Step 4: Restart Your Server
1. Stop the current server (press Ctrl+C in terminal)
2. Start it again:
   ```bash
   python main.py
   ```

### Step 5: Test Again
- Go back to http://localhost:8000
- Try sending a message
- It should now work within 5-10 seconds!

## Troubleshooting

### Still getting "User not found"?
- Copy the key again (make sure you have the FULL key)
- No spaces or extra characters
- Save the .env file
- Restart the server

### Still hanging after restart?
- Check the server logs for `[SERVICE] AUTHENTICATION ERROR`
- Verify the key is valid on OpenRouter's website
- Try using a different model (edit main.py if needed)

## What's Happening

When an API key is invalid:
1. ❌ Request reaches your frontend
2. ❌ Goes to `/a2a/motivation` endpoint  
3. ❌ Hits `[SERVICE] Making API call...`
4. ❌ OpenRouter rejects with 401 (User not found)
5. ❌ Error handling catches it and returns fallback (or hangs)
6. ❌ Frontend waits 5+ minutes for response

With the updated error handling, you should see:
```
[SERVICE] AUTHENTICATION ERROR - API key invalid: Error code: 401
[SERVICE] Please update OPENAI_API_KEY in .env file
```

Then the fallback motivation will be used instead.

