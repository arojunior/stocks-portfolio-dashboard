# Meta Graph API Explorer - Visual Guide

## 🎯 **Step-by-Step Visual Guide**

### Step 1: Open Graph API Explorer
1. Go to: https://developers.facebook.com/tools/explorer/
2. Make sure you're logged into Facebook

### Step 2: Select Your App
1. Look for the dropdown in the top-right corner
2. Click on it and select your app: **Portfolio Dashboard**
3. You should see your App ID: `2753087221690068`

### Step 3: Generate Access Token
1. Click the **"Generate Access Token"** button (blue button)
2. A popup will appear with permission checkboxes
3. **Check these permissions**:
   - ✅ `threads_basic`
   - ✅ `threads_content_publish`
   - ✅ `threads_manage_replies`
   - ✅ `threads_read_replies`
   - ✅ `threads_manage_insights`
4. Click **"Generate Access Token"**

### Step 4: Copy the Token
1. You'll see a long string in the "Access Token" field
2. It looks like: `EAABwzL...` (starts with EAABwzL)
3. **Copy this entire string**

### Step 5: Test the Token
1. Change the endpoint from `me` to `me/threads`
2. Click **"Submit"**
3. If you see data or an empty array `[]`, the token works!

## 🔧 **Update Your .env File**

1. Open your `.env` file
2. Find the line: `META_ACCESS_TOKEN=94c483ea57952da046492b2f17102576`
3. Replace it with: `META_ACCESS_TOKEN=EAABwzL...your_new_token_here`
4. Save the file

## 🧪 **Test Your Token**

Run this command to test:

```bash
python3 tests/quick_token_test.py
```

## ⚠️ **Common Issues**

### Issue: "App not approved"
**Solution**: 
1. Go to your app settings
2. Change from "Live" to "Development" mode
3. Try generating the token again

### Issue: "Insufficient permissions"
**Solution**:
1. Make sure you selected ALL the required permissions
2. Regenerate the token with all permissions checked

### Issue: "User not authorized"
**Solution**:
1. Go to your app → Roles → Add People
2. Add yourself as a test user
3. Try generating the token again

## 🚀 **Quick Test Commands**

Test your token with these commands:

```bash
# Test basic API
curl "https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN_HERE"

# Test threads endpoint
curl "https://graph.threads.net/v1.0/me/threads?access_token=YOUR_TOKEN_HERE"
```

## 📱 **What You Should See**

### Successful Response:
```json
{
  "id": "123456789",
  "username": "your_username"
}
```

### Threads Response:
```json
{
  "data": [
    {
      "id": "thread_id",
      "text": "Your thread content...",
      "created_time": "2024-01-01T00:00:00+0000"
    }
  ]
}
```

## 🆘 **Still Having Trouble?**

If you're still having issues:

1. **Check App Status**: Make sure your app is in "Development" mode
2. **Check Permissions**: Ensure you have all required permissions
3. **Check Token Format**: Should start with "EAABwzL..."
4. **Check Expiration**: Token expires in 1-2 hours

## 💡 **Pro Tips**

1. **Bookmark the Explorer**: Save the Graph API Explorer for easy access
2. **Test Regularly**: Tokens expire, so test before using
3. **Use Development Mode**: Keep your app in Development mode for testing
4. **Check Logs**: Use the Meta Developer Dashboard to see API call logs

---

**Need More Help?** If you're still stuck, let me know what error you're seeing and I'll help you troubleshoot!
