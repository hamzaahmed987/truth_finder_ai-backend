# 🤖 Truth Finder AI Agent Setup Guide (Gemini Version)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd back_end
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the `back_end` directory:
```bash
# Required for AI Agent (Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Existing keys (if you have them)
TWITTER_BEARER_TOKEN=your_twitter_token_here
```

### 3. Get Google API Key (for Gemini)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Paste it in your `.env` file

### 4. Test Your Agent
```bash
cd back_end
python test_agent.py
```

### 5. Start the Server
```bash
cd back_end
python run_server.py
```

## 🎯 What Your AI Agent Can Do

### ✅ **Advanced News Analysis**
- 🔍 **Comprehensive Fact-Checking** - Uses Gemini 1.5 Flash for detailed analysis
- 📊 **Confidence Scoring** - Provides confidence levels (0-100%)
- 🎯 **Smart Verdicts** - REAL/FAKE/PROPAGANDA/SUSPICIOUS
- 🌍 **Multi-Language Support** - English and Urdu/Hindi
- 📈 **Analysis History** - Stores previous analyses

### 🛠️ **Available Tools** (Ready for Integration)
- 🔍 **Web Search** - Find related information
- 💭 **Sentiment Analysis** - Analyze text sentiment using Gemini
- ✅ **Fact Checking** - Verify claims against sources
- 📚 **Source Credibility** - Evaluate source reliability
- 🐦 **Twitter Sentiment** - Get public opinion

## 📡 API Endpoints

### New AI Agent Endpoints:
- **`POST /agent/analyze`** - Single AI agent analysis
- **`POST /agent/multi-analyze`** - Multi-agent system analysis
- **`GET /agent/status`** - Check agent system status

### Example Usage:
```bash
curl -X POST "http://localhost:8000/agent/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your news content here",
    "language": "english"
  }'
```

## 🎨 Frontend Integration

Your frontend now has:
- ✅ **AI Agent Toggle** - Switch between regular and AI agent analysis
- 🤖 **Enhanced UI** - Better results display with confidence scores
- 🎯 **Verdict Indicators** - Color-coded results (Real/Fake/Propaganda/Suspicious)
- 📊 **Detailed Analysis** - Comprehensive breakdown of findings

## 🔧 Advanced Configuration

### Customizing the Agent
Edit `app/agents.py` to:
- Modify analysis prompts
- Add new tools
- Change confidence thresholds
- Customize verdict logic

### Adding New Tools
```python
async def your_custom_tool(self, input_data: str) -> str:
    """Your custom analysis tool"""
    # Your implementation here
    return "Analysis result"
```

## 🚨 Troubleshooting

### Common Issues:

1. **"GOOGLE_API_KEY not found"**
   - Make sure you have a `.env` file in the `back_end` directory
   - Verify your API key is correct
   - Check that you have access to Gemini API

2. **"Module not found" errors**
   - Run `pip install -r requirements.txt`
   - Make sure you're in the `back_end` directory

3. **Server won't start**
   - Check if port 8000 is available
   - Try `python run_server.py` from the `back_end` directory

4. **Agent analysis fails**
   - Check your internet connection
   - Verify Google API key is valid
   - Check Gemini service status

## 🎉 Success Indicators

When everything is working:
- ✅ `python test_agent.py` runs without errors
- ✅ Server starts on `http://localhost:8000`
- ✅ `/agent/status` returns agent information
- ✅ Frontend can use AI agent analysis
- ✅ You see "✅ Gemini API configured successfully" when starting

## 🔮 Next Steps

1. **Integrate Real APIs** - Replace placeholders with actual search/fact-check APIs
2. **Add More Agents** - Specialized agents for different analysis types
3. **Agent Memory** - Store analysis history for learning
4. **Real-time Updates** - Live analysis as news develops

---

**🎯 Your Truth Finder AI is now powered by Google Gemini AI agents!** 