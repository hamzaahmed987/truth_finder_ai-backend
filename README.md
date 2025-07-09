# 🤖 Truth Finder AI - Complete Setup Guide

## 🚨 **CRITICAL ISSUES FIXED**

Your Truth Finder AI project had several major issues that prevented it from working properly. This guide will help you fix them all.

## 🔧 **Step 1: Set Up Environment Variables**

Create a `.env` file in the `back_end` directory:

```bash
# Required: Google Gemini API Key (for AI analysis)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional: Twitter API (for sentiment analysis)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Optional: Google Custom Search API (for fact checking)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Backend Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

## 🔑 **Step 2: Get Required API Keys**

### **Google Gemini API Key (REQUIRED)**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and paste it in your `.env` file

### **Twitter API Key (Optional)**
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for a developer account
3. Create a new app
4. Get your Bearer Token
5. Add it to your `.env` file

### **Google Custom Search API (Optional)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Custom Search API
3. Create credentials
4. Create a Custom Search Engine at [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Add both keys to your `.env` file

## 🚀 **Step 3: Install Dependencies**

```bash
cd back_end
pip install -r requirements.txt
```

## 🧪 **Step 4: Test Your Setup**

```bash
cd back_end
python test_agent.py
```

You should see:
```
✅ Gemini API configured successfully
🤖 Testing Truth Finder AI Agent (Gemini Version)...
✅ Analysis Complete!
🎯 Verdict: SUSPICIOUS
📊 Confidence: 75%
```

## 🌐 **Step 5: Start the Backend Server**

```bash
cd back_end
python run_server.py
```

Your server should start on `http://localhost:8000`

## 🎨 **Step 6: Start the Frontend**

```bash
cd front_end
npm install
npm run dev
```

Your frontend should start on `http://localhost:3000`

## 🔍 **What Was Fixed**

### **1. Missing API Integration**
- ❌ **Before**: All functions were placeholders returning dummy data
- ✅ **After**: Real integration with Google Gemini API for AI analysis

### **2. Basic Analysis Logic**
- ❌ **Before**: Only checked for keywords like "fake" or "hoax"
- ✅ **After**: Comprehensive AI-powered analysis with confidence scoring

### **3. Twitter Sentiment Analysis**
- ❌ **Before**: Hardcoded dummy tweets
- ✅ **After**: Real Twitter API integration (when configured)

### **4. Error Handling**
- ❌ **Before**: Poor error handling and unclear messages
- ✅ **After**: Clear error messages and fallback responses

### **5. Language Support**
- ❌ **Before**: Basic language detection
- ✅ **After**: Enhanced multi-language support with proper prompts

## 🎯 **How to Use**

### **Frontend Usage:**
1. Go to `http://localhost:3000`
2. Check "🤖 Use Advanced AI Agent (Recommended)"
3. Paste your news content or URL
4. Click "🤖 AI Agent Analyze"
5. Get detailed analysis with confidence scores

### **API Usage:**
```bash
curl -X POST "http://localhost:8000/agent/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your news content here",
    "language": "english"
  }'
```

## 🚨 **Troubleshooting**

### **"Google API key not configured"**
- Make sure you have a `.env` file in the `back_end` directory
- Verify your Google API key is correct
- Check that you have access to Gemini API

### **"Module not found" errors**
- Run `pip install -r requirements.txt`
- Make sure you're in the `back_end` directory

### **"Twitter API not configured"**
- This is optional - the system will work without it
- If you want Twitter sentiment, add your Twitter Bearer Token to `.env`

### **Frontend can't connect to backend**
- Make sure backend is running on port 8000
- Check that `NEXT_PUBLIC_API_URL` is set correctly in frontend

## 🎉 **Success Indicators**

When everything is working:
- ✅ `python test_agent.py` runs without errors
- ✅ Server starts on `http://localhost:8000`
- ✅ `/agent/status` returns agent information
- ✅ Frontend can use AI agent analysis
- ✅ You see detailed analysis with confidence scores

## 🔮 **Next Steps**

1. **Add More APIs**: Integrate with fact-checking websites
2. **Improve Analysis**: Add more specialized agents
3. **Add Database**: Store analysis history
4. **Real-time Updates**: Live analysis as news develops

---

**🎯 Your Truth Finder AI is now fully functional with real AI analysis!** 