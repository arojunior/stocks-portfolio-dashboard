# Meta Threads OAuth Setup Guide

## 🔍 **Current Issue**

The Meta Threads API is returning: `"Invalid OAuth access token - Cannot parse access token"`

This means the access token you provided is not in the correct format. Meta Threads API requires a **user access token** obtained through OAuth flow, not an app access token.

## 🎯 **What You Need**

1. **User Access Token**: Generated through OAuth flow
2. **Proper Permissions**: `threads_basic`, `threads_content_publish`, etc.
3. **OAuth Redirect URI**: For the authorization flow

## 🔧 **Step-by-Step OAuth Setup**

### 1. **Configure OAuth in Meta Developer Dashboard**

1. Go to your Meta app: [developers.facebook.com](https://developers.facebook.com/)
2. Navigate to **Products** → **Threads API**
3. Click **Set Up** on the Threads API
4. Configure OAuth settings:
   - **Valid OAuth Redirect URIs**: Add your app's redirect URI
   - **App Domains**: Add your domain
   - **Website**: Add your website URL

### 2. **Set Up OAuth Flow in Your App**

Create a new file `core/threads_oauth.py`:

```python
import os
import requests
from urllib.parse import urlencode, parse_qs
import streamlit as st

class ThreadsOAuth:
    def __init__(self):
        self.app_id = os.getenv("META_APP_ID")
        self.app_secret = os.getenv("META_APP_SECRET")
        self.redirect_uri = "http://localhost:8501/threads_callback"  # Your Streamlit app URL
        
    def get_auth_url(self):
        """Generate OAuth authorization URL"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "threads_basic,threads_content_publish",
            "response_type": "code"
        }
        
        return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_long_lived_token(self, short_token):
        """Exchange short-lived token for long-lived token"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
```

### 3. **Add OAuth Flow to Your Streamlit App**

Add this to your `app/main.py`:

```python
# Add OAuth flow for Threads
if st.sidebar.button("🔗 Connect Threads"):
    oauth = ThreadsOAuth()
    auth_url = oauth.get_auth_url()
    st.sidebar.markdown(f"[Connect to Threads]({auth_url})")

# Handle OAuth callback
if "code" in st.query_params:
    oauth = ThreadsOAuth()
    code = st.query_params["code"]
    
    try:
        token_data = oauth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        # Store token securely
        st.session_state["threads_access_token"] = access_token
        st.success("✅ Threads connected successfully!")
        
    except Exception as e:
        st.error(f"❌ Threads connection failed: {e}")
```

### 4. **Update Threads Integration**

Update `core/social_fetcher.py`:

```python
def fetch_threads_mentions(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch Meta Threads mentions for a stock ticker"""
    try:
        # Get token from session state (OAuth flow)
        access_token = st.session_state.get("threads_access_token")
        
        if not access_token:
            print(f"No Threads access token found for {ticker}")
            return []
        
        # Now use the proper user access token
        url = "https://graph.threads.net/v1.0/me/threads"
        params = {
            "access_token": access_token,
            "fields": "id,text,created_time,like_count,reply_count,repost_count",
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Process the data...
            return process_threads_data(data, ticker)
        else:
            print(f"Threads API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching Threads data for {ticker}: {e}")
        return []
```

## 🚀 **Alternative: Use Meta Graph API Explorer**

If OAuth setup is complex, you can use the Meta Graph API Explorer:

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Generate a user access token
4. Test the Threads API endpoints
5. Copy the working token to your `.env` file

## 📋 **Required Permissions**

Make sure your Meta app has these permissions:
- `threads_basic` - Read basic profile information
- `threads_content_publish` - Publish content
- `threads_manage_replies` - Manage replies
- `threads_read_replies` - Read replies
- `threads_manage_insights` - Access analytics

## 🔍 **Testing Your Setup**

1. **Test OAuth Flow**: Make sure the authorization URL works
2. **Test Token Exchange**: Verify you can exchange code for token
3. **Test API Calls**: Use the token to make actual API calls
4. **Test Permissions**: Ensure you have the right permissions

## 💡 **Quick Fix for Testing**

For immediate testing, you can:

1. Use the Meta Graph API Explorer to generate a test token
2. Replace your current token with the test token
3. Test the integration
4. Set up proper OAuth later

## 🆘 **Troubleshooting**

### Common Issues:

1. **"Invalid OAuth access token"**: Token format is wrong
2. **"Insufficient permissions"**: Missing required permissions
3. **"App not approved"**: App needs to be approved for production
4. **"Rate limit exceeded"**: Too many API calls

### Debug Steps:

1. Check token format in Graph API Explorer
2. Verify app permissions in Developer Dashboard
3. Test API endpoints manually
4. Check rate limits and usage

---

**Next Steps**: Set up the OAuth flow as described above, or use the Graph API Explorer to generate a proper user access token for testing.
