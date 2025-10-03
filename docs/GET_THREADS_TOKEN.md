# How to Get Meta Threads Access Token - Step by Step

## 🎯 **Easy Method: Meta Graph API Explorer**

### Step 1: Go to Graph API Explorer
1. Open your browser and go to: https://developers.facebook.com/tools/explorer/
2. Make sure you're logged into your Facebook account

### Step 2: Select Your App
1. In the top-right corner, click the dropdown that says "Graph API Explorer"
2. Select your app: **Portfolio Dashboard** (or whatever you named it)
3. You should see your App ID: `2753087221690068`

### Step 3: Generate Access Token
1. Click the **"Generate Access Token"** button
2. A popup will appear asking for permissions
3. **IMPORTANT**: Make sure to select these permissions:
   - ✅ `threads_basic`
   - ✅ `threads_content_publish`
   - ✅ `threads_manage_replies`
   - ✅ `threads_read_replies`
   - ✅ `threads_manage_insights`
4. Click **"Generate Access Token"**

### Step 4: Copy the Token
1. You'll see a long string that starts with something like: `EAABwzL...`
2. **Copy this entire token** - it's your user access token
3. This token will be valid for about 1-2 hours

### Step 5: Test the Token
1. In the Graph API Explorer, change the endpoint to: `me/threads`
2. Click **"Submit"**
3. If you see data, your token works!

## 🔧 **Update Your .env File**

Replace your current `META_ACCESS_TOKEN` with the new token:

```bash
# In your .env file
META_ACCESS_TOKEN=EAABwzL...your_new_token_here
```

## 🧪 **Test the Integration**

Run this command to test:

```bash
python3 tests/test_threads_integration.py
```

## ⚠️ **Important Notes**

1. **Token Expires**: The token expires in 1-2 hours
2. **Permissions**: Make sure you have the right permissions
3. **App Status**: Your app needs to be in "Development" mode
4. **Test Users**: You might need to add yourself as a test user

## 🆘 **If You Get Errors**

### Error: "App not approved"
- Your app is in "Live" mode but not approved
- Switch to "Development" mode in your app settings

### Error: "Insufficient permissions"
- You didn't select all the required permissions
- Go back and regenerate the token with all permissions

### Error: "User not authorized"
- You need to add yourself as a test user
- Go to your app → Roles → Add People → Test Users

## 🚀 **Alternative: Use Facebook Login**

If the Graph API Explorer doesn't work, you can use Facebook Login:

1. Go to your app → Products → Facebook Login
2. Set up Facebook Login
3. Use the login flow to get a user token
4. This is more complex but more reliable

## 📱 **Quick Test**

Once you have the token, test it with this simple command:

```bash
curl "https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN_HERE"
```

If you get a response with your user info, the token works!

---

**Need Help?** If you're still having trouble, let me know what error you're seeing and I'll help you troubleshoot!
