# Meta Threads Integration Guide

## 🎯 Overview

This guide explains how to integrate Meta Threads as a free social media source for your portfolio dashboard.

## ✅ Why Threads?

- **✅ Free API**: No paid tiers or subscription costs
- **✅ Real Social Data**: Access to actual Threads posts and mentions
- **✅ Engagement Metrics**: Likes, replies, reposts, quotes
- **✅ Public Content**: Search for stock mentions and sentiment
- **✅ Rate Limits**: Reasonable free tier limits

## 🔧 Setup Steps

### 1. Create Meta Developer Account

1. Visit [developers.facebook.com](https://developers.facebook.com/)
2. Sign up for a Meta Developer account
3. Verify your account (may require phone number)

### 2. Create Threads App

1. In the Developer Dashboard, click "Create App"
2. Select "Business" as the app type
3. Choose "Access the Threads API" as the use case
4. Fill in app details:
   - **App Name**: "Portfolio Dashboard"
   - **App Contact Email**: Your email
   - **Business Account**: Link to your business account

### 3. Configure App Permissions

Enable these permissions in your app:
- `threads_basic` - Read basic profile information
- `threads_content_publish` - Publish content (if needed)
- `threads_manage_insights` - Access analytics

### 4. Set Up OAuth

1. Go to "Products" → "Threads API"
2. Configure OAuth redirect URIs
3. Set up authentication flow
4. Generate access tokens

### 5. Add Testers

1. Invite Threads users as testers
2. They need to accept the invitation
3. This grants your app permission to access their data

## 🔑 Environment Variables

Add these to your `.env` file:

```bash
# Meta Threads API
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_ACCESS_TOKEN=your_access_token_here
```

## 📝 API Implementation

### Basic Threads API Usage

```python
import requests

def fetch_threads_mentions(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch Meta Threads mentions for a stock ticker"""
    try:
        access_token = os.getenv("META_ACCESS_TOKEN")
        if not access_token:
            print("Meta access token not found")
            return []
        
        # Search for mentions of the ticker
        url = f"https://graph.threads.net/v1.0/me/threads"
        params = {
            "access_token": access_token,
            "fields": "id,text,created_time,like_count,reply_count,repost_count",
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filter for ticker mentions
        mentions = []
        for thread in data.get("data", []):
            if ticker.lower() in thread.get("text", "").lower():
                mentions.append({
                    "text": thread.get("text", ""),
                    "author": "Threads User",  # Would need additional API call
                    "created_at": thread.get("created_time", ""),
                    "like_count": thread.get("like_count", 0),
                    "reply_count": thread.get("reply_count", 0),
                    "repost_count": thread.get("repost_count", 0),
                    "url": f"https://threads.net/thread/{thread.get('id', '')}",
                    "source": "Threads"
                })
        
        return mentions
        
    except Exception as e:
        print(f"Error fetching Threads data for {ticker}: {e}")
        return []
```

## 🚀 Features You Can Implement

### 1. Stock Mention Search
- Search for posts mentioning your portfolio stocks
- Filter by date range and engagement
- Get real-time social sentiment

### 2. Engagement Metrics
- Track likes, replies, reposts, quotes
- Monitor social media buzz around stocks
- Identify trending discussions

### 3. Sentiment Analysis
- Analyze post content for positive/negative sentiment
- Track sentiment changes over time
- Correlate social sentiment with stock performance

### 4. User Insights
- Identify influential users discussing your stocks
- Track expert opinions and analysis
- Monitor community discussions

## 📊 Rate Limits

Meta Threads API has reasonable rate limits:
- **Basic Tier**: 200 requests per hour
- **Standard Tier**: 1,000 requests per hour
- **Premium Tier**: 10,000 requests per hour

For a portfolio dashboard, the basic tier should be sufficient.

## 🔒 Privacy & Compliance

- Only access public posts and data
- Respect user privacy settings
- Follow Meta's terms of service
- Implement proper data handling

## 🎯 Next Steps

1. **Set up your Meta Developer account**
2. **Create a Threads app with the required permissions**
3. **Add your API credentials to the `.env` file**
4. **Test the integration with a few stocks**
5. **Monitor rate limits and optimize API usage**

## 💡 Pro Tips

- **Cache Results**: Store API responses to avoid hitting rate limits
- **Batch Requests**: Combine multiple searches into single requests
- **Error Handling**: Implement robust error handling for API failures
- **Fallback**: Always have a fallback if Threads API is unavailable

## 🆘 Troubleshooting

### Common Issues:

1. **"Invalid Access Token"**: Check your token and permissions
2. **"Rate Limit Exceeded"**: Implement caching and request throttling
3. **"Permission Denied"**: Ensure your app has the right permissions
4. **"No Data Returned"**: Check if the search terms are too specific

### Debug Steps:

1. Test your access token with a simple API call
2. Check your app permissions in the Meta Developer Dashboard
3. Verify your OAuth configuration
4. Review the API documentation for any changes

## 📚 Resources

- [Meta Threads API Documentation](https://developers.facebook.com/docs/threads/)
- [Threads API Getting Started](https://developers.facebook.com/docs/threads/get-started/)
- [Meta Developer Community](https://developers.facebook.com/community/)
- [Threads API Rate Limits](https://developers.facebook.com/docs/threads/rate-limits/)

---

**Ready to integrate Threads?** Follow the setup steps above and you'll have real social media data in your portfolio dashboard! 🚀
