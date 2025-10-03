# Meta Threads Integration Setup Guide

## 🎯 **Overview**

This guide explains how to set up Meta Threads integration for your portfolio dashboard. Meta Threads API provides free access to social media data from Threads posts.

## 🔧 **Quick Setup (Recommended)**

### Step 1: Get Access Token via Graph API Explorer

1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your app**: Portfolio Dashboard (App ID: 2753087221690068)
3. **Click "Generate Access Token"**
4. **Select these permissions**:
   - ✅ `threads_basic`
   - ✅ `threads_content_publish`
   - ✅ `threads_manage_replies`
   - ✅ `threads_read_replies`
   - ✅ `threads_manage_insights`
5. **Copy the token** (starts with `EAABwzL...`)

### Step 2: Update Environment Variables

Add to your `.env` file:
```bash
META_APP_ID=2753087221690068
META_ACCESS_TOKEN=EAABwzL...your_token_here
```

### Step 3: Test the Integration

```bash
python3 tests/quick_token_test.py
```

## 🧪 **Testing**

### Quick Token Test
```bash
python3 tests/quick_token_test.py
```

### Full Integration Test
```bash
python3 tests/test_threads_integration.py
```

## 🆘 **Troubleshooting**

### Common Issues

**"Invalid OAuth access token"**
- **Cause**: Wrong token format (App token instead of User token)
- **Fix**: Use Graph API Explorer to generate User token

**"App not approved"**
- **Cause**: App is in Live mode but not approved
- **Fix**: Switch to Development mode in app settings

**"Insufficient permissions"**
- **Cause**: Missing required permissions
- **Fix**: Regenerate token with all permissions selected

**"User not authorized"**
- **Cause**: Not added as test user
- **Fix**: Add yourself as test user in app roles

### Token Format Check

**❌ Wrong (App Access Token):**
- `1548496402818134|E1K...`
- `123456789|ABC...`

**✅ Correct (User Access Token):**
- `EAABwzL...`
- `EAABwzL...`

## 🔧 **Advanced Setup (OAuth Flow)**

If you need a more robust solution, you can implement OAuth flow:

### 1. Configure OAuth in Meta Developer Dashboard

1. Go to your app → Products → Threads API
2. Set up OAuth redirect URIs
3. Configure app domains

### 2. Implement OAuth in Your App

```python
class ThreadsOAuth:
    def __init__(self):
        self.app_id = os.getenv("META_APP_ID")
        self.app_secret = os.getenv("META_APP_SECRET")
        self.redirect_uri = "http://localhost:8501/threads_callback"
        
    def get_auth_url(self):
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "threads_basic,threads_content_publish",
            "response_type": "code"
        }
        return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
```

## 📊 **Features Available**

Once set up, you'll have access to:

- **Threads Posts**: Search for stock mentions
- **Engagement Metrics**: Likes, replies, reposts
- **Social Sentiment**: Analyze post content
- **Real-time Data**: Latest discussions about your stocks

## 🚀 **Usage in Your App**

The integration is already implemented in your dashboard:

- **Social Media Tab**: Shows Threads posts about your stocks
- **Sentiment Analysis**: Analyzes social sentiment
- **Engagement Metrics**: Displays likes, replies, reposts

## 📚 **API Reference**

### Endpoints Used

- `GET /me` - Get user profile
- `GET /me/threads` - Get user's threads
- `GET /me/threads/{thread-id}` - Get specific thread

### Rate Limits

- **Basic Tier**: 200 requests per hour
- **Standard Tier**: 1,000 requests per hour
- **Premium Tier**: 10,000 requests per hour

## 💡 **Best Practices**

1. **Cache Results**: Store API responses to avoid rate limits
2. **Error Handling**: Implement robust error handling
3. **Rate Limiting**: Respect API rate limits
4. **Token Management**: Handle token expiration

## 🔍 **Debug Commands**

```bash
# Test basic API
curl "https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN"

# Test threads endpoint
curl "https://graph.threads.net/v1.0/me/threads?access_token=YOUR_TOKEN"
```

---

**Ready to set up?** Follow the Quick Setup steps above to get started with Meta Threads integration!
