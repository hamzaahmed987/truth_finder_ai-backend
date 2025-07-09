import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import tweepy # type: ignore
from textblob import TextBlob # type: ignore
import re
import asyncio
from typing import Dict, List, Optional, Any

# Load environment variables
load_dotenv()

# Configure APIs
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        print("✅ Gemini API configured successfully")
    else:
        print("⚠️  Warning: GOOGLE_API_KEY not found")
        model = None
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")
    model = None

# Twitter API setup (optional)
try:
    twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
    if twitter_token:
        client = tweepy.Client(bearer_token=twitter_token)
        print("✅ Twitter API configured successfully")
    else:
        print("⚠️  Warning: TWITTER_BEARER_TOKEN not found")
        client = None
except Exception as e:
    print(f"❌ Error configuring Twitter: {e}")
    client = None

def detect_language(text):
    """Language detect karta hai based on script and common words"""
    # Urdu/Arabic script check
    urdu_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    # Hindi/Devanagari script check  
    hindi_pattern = r'[\u0900-\u097F]'
    
    # Common Urdu/Hindi words in Roman
    urdu_hindi_words = ['hai', 'hy', 'aur', 'ka', 'ki', 'ke', 'se', 'mein', 'kya', 'yeh', 'wo', 'hum', 'tum', 'ap', 'koi', 'sab']
    
    text_lower = text.lower()
    
    if re.search(urdu_pattern, text) or re.search(hindi_pattern, text):
        return 'urdu_hindi'
    elif any(word in text_lower for word in urdu_hindi_words):
        return 'urdu_hindi'
    else:
        return 'english'

def get_response_templates(lang):
    """Language-specific response templates with emojis"""
    if lang == 'urdu_hindi':
        return {
            'analyzing': "🔍 **News Ka Analysis Chal Raha Hai...** 📊",
            'ai_title': "🤖 **AI Expert Ki Detailed Ray:**",
            'sentiment_title': "💭 **Awaam Ka Overall Mood:**", 
            'tweets_title': "📱 **Log Kya Keh Rahe Hain:**",
            'verdict_title': "🚨 **FINAL JUDGMENT - YE KYA HAI?**",
            'real': "✅ **REAL NEWS HAI** - Bharosa kar sakte hain! 💯",
            'fake': "❌ **FAKE NEWS HAI** - Bilkul jhuta! ⚠️", 
            'propaganda': "⚠️ **PROPAGANDA HAI** - Kisi ka agenda push kar rahe! 🎭",
            'suspicious': "🤔 **SUSPICIOUS HAI** - Carefully dekho! 👀"
        }
    else:
        return {
            'analyzing': "🔍 **Analyzing News Content...** 📊",
            'ai_title': "🤖 **AI Expert Analysis:**",
            'sentiment_title': "💭 **Public Sentiment Overview:**",
            'tweets_title': "📱 **What People Are Saying:**", 
            'verdict_title': "🚨 **FINAL VERDICT - WHAT IS THIS?**",
            'real': "✅ **REAL NEWS** - You can trust this! 💯",
            'fake': "❌ **FAKE NEWS** - Completely false! ⚠️",
            'propaganda': "⚠️ **PROPAGANDA** - Someone's pushing agenda! 🎭", 
            'suspicious': "🤔 **SUSPICIOUS** - Be careful! 👀"
        }

def create_enhanced_prompt(text, lang):
    """Enhanced Gemini prompt with better instructions"""
    
    if lang == 'urdu_hindi':
        return f"""
🔍 **NEWS VERIFICATION ANALYSIS** 🔍

Ye news analyze karo detail mein: "{text}"

**ANALYSIS KARNEY KE LIYE:**
1. ✅ Factual accuracy check karo - kya ye sach hai?
2. 🔍 Sources ki credibility dekho - reliable hain ya nahi?
3. ⚠️ Propaganda patterns dhundo - koi agenda push kar rahe?
4. 📊 Misinformation signs check karo - typical fake news markers
5. 🎯 Emotional manipulation dekho - unnecessarily dramatic language?
6. 📰 Cross-verification - dusre sources mein same news hai?

**RESPONSE FORMAT (Urdu/Hindi mein attractive style mein):**
📋 **News Summary:** (2-3 lines mein kya keh rahi ye news)
🔍 **Detailed Analysis:** (Step by step reasoning with facts)
📚 **Sources Status:** (Reliable sources mention hain ya nahi)
🎯 **Red Flags:** (Agar koi suspicious cheezein hain)
⚖️ **Final Judgment:** (REAL/FAKE/PROPAGANDA/SUSPICIOUS - with confidence level)

**Response bilkul ek dost ki tarah simple language mein dena with emojis!**
"""
    else:
        return f"""
🔍 **NEWS VERIFICATION ANALYSIS** 🔍

Please analyze this news in detail: "{text}"

**ANALYSIS REQUIREMENTS:**
1. ✅ Check factual accuracy - is this actually true?
2. 🔍 Verify source credibility - are sources reliable?
3. ⚠️ Look for propaganda patterns - any agenda being pushed?
4. 📊 Check misinformation signs - typical fake news markers
5. 🎯 Spot emotional manipulation - unnecessarily dramatic language?
6. 📰 Cross-verification - does this appear in other reliable sources?

**RESPONSE FORMAT (in engaging conversational style):**
📋 **News Summary:** (2-3 lines about what this news claims)
🔍 **Detailed Analysis:** (Step by step reasoning with facts)
📚 **Sources Status:** (Are reliable sources mentioned or not)
🎯 **Red Flags:** (Any suspicious elements found)
⚖️ **Final Judgment:** (REAL/FAKE/PROPAGANDA/SUSPICIOUS - with confidence level)

**Keep response friendly and conversational with emojis!**
"""

async def get_real_twitter_sentiment(topic: str) -> List[str]:
    """Get real Twitter sentiment for a topic"""
    if not client:
        return ["Twitter API not configured - no sentiment data available"]
    
    try:
        # Search for tweets about the topic
        query = f"{topic} -is:retweet lang:en"
        tweets = client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if not tweets.data:
            return ["No recent tweets found about this topic"]
        
        # Extract tweet text
        tweet_texts = [tweet.text for tweet in tweets.data[:5]]
        return tweet_texts
        
    except Exception as e:
        return [f"Twitter sentiment analysis failed: {str(e)}"]

async def analyze_sentiment_with_ai(text: str) -> str:
    """Analyze sentiment using Gemini AI"""
    if not model:
        return "Sentiment analysis failed: AI model not configured"
    
    try:
        prompt = f"""
        Analyze the sentiment of this text and return ONLY one word: POSITIVE, NEGATIVE, or NEUTRAL.
        
        Text: "{text}"
        
        Consider:
        - Emotional language
        - Tone of voice
        - Overall message
        
        Return only: POSITIVE, NEGATIVE, or NEUTRAL
        """
        
        response = model.generate_content(prompt)
        sentiment = response.text.strip().upper()
        
        if sentiment in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
            return sentiment
        else:
            return "NEUTRAL"
            
    except Exception as e:
        return f"Sentiment analysis failed: {str(e)}"

async def search_web_for_facts(query: str) -> List[str]:
    """Search web for fact verification (placeholder for now)"""
    try:
        # This would integrate with a search API like Google Custom Search
        # For now, return a placeholder
        return [
            f"Web search for '{query}' would be performed here",
            "Integration with search API needed for real fact checking"
        ]
    except Exception as e:
        return [f"Web search failed: {str(e)}"]

def analyze_news(text: str) -> dict:
    """
    Analyze the given news text and return detailed analysis info.
    """
    try:
        # 1. Language detection
        detected_language = detect_language(text)
        
        # 2. AI Analysis using Gemini
        ai_analysis = ""
        confidence = 50  # Default confidence
        
        if model:
            try:
                prompt = create_enhanced_prompt(text, detected_language)
                response = model.generate_content(prompt)
                ai_analysis = response.text
                
                # Extract confidence from AI response
                confidence_match = re.search(r'confidence[:\s]*(\d+)', ai_analysis.lower())
                if confidence_match:
                    confidence = int(confidence_match.group(1))
                else:
                    # Estimate confidence based on response length and content
                    confidence = min(95, max(20, len(ai_analysis) // 10))
                    
            except Exception as e:
                ai_analysis = f"AI analysis failed: {str(e)}"
                confidence = 30
        else:
            ai_analysis = "AI analysis not available - API key not configured"
            confidence = 20
        
        # 3. Determine if fake based on AI analysis
        ai_lower = ai_analysis.lower()
        is_fake = any(word in ai_lower for word in ['fake', 'false', 'misinformation', 'jhoot', 'galat'])
        
        # 4. Get sentiment analysis
        sentiment = "Neutral"  # Default
        if model:
            try:
                sentiment = asyncio.run(analyze_sentiment_with_ai(text))
            except:
                pass
        
        # 5. Get sample tweets (async)
        sample_tweets = []
        try:
            sample_tweets = asyncio.run(get_real_twitter_sentiment(text[:100]))
        except:
            sample_tweets = ["Twitter analysis not available"]
        
        # 6. Generate sources (placeholder for now)
        sources = [
            "AI Analysis: Google Gemini",
            "Sentiment Analysis: TextBlob + AI",
            "Fact Checking: Manual verification needed"
        ]
        
        # 7. Create complete response
        templates = get_response_templates(detected_language)
        
        complete_response = f"""
{templates['analyzing']}

{templates['ai_title']}
{ai_analysis}

{templates['sentiment_title']}
{sentiment}

{templates['tweets_title']}"""
        
        # Add sample tweets
        for tweet in sample_tweets[:3]:
            complete_response += f"\n💬 {tweet[:120]}{'...' if len(tweet) > 120 else ''}"
        
        # Add final verdict
        if is_fake:
            complete_response += f"\n\n{templates['verdict_title']}\n{templates['fake']}"
        elif 'propaganda' in ai_lower:
            complete_response += f"\n\n{templates['verdict_title']}\n{templates['propaganda']}"
        elif 'real' in ai_lower and 'fake' not in ai_lower:
            complete_response += f"\n\n{templates['verdict_title']}\n{templates['real']}"
        else:
            complete_response += f"\n\n{templates['verdict_title']}\n{templates['suspicious']}"
        
        # Construct the response dictionary
        response = {
            "is_fake": is_fake,
            "confidence": confidence / 100,  # Convert to 0-1 scale
            "analysis": ai_analysis,
            "sources": sources,
            "public_sentiment": sentiment,
            "detected_language": detected_language,
            "sample_tweets": sample_tweets,
            "complete_response": complete_response
        }
        
        return response
        
    except Exception as e:
        # Fallback response if everything fails
        return {
            "is_fake": False,
            "confidence": 0.1,
            "analysis": f"Analysis failed: {str(e)}",
            "sources": [],
            "public_sentiment": "Unknown",
            "detected_language": "english",
            "sample_tweets": ["Analysis failed"],
            "complete_response": f"❌ Analysis failed: {str(e)}\n\nPlease check your API configuration and try again."
        }

# Usage example
if __name__ == "__main__":
    # Test the enhanced analysis
    test_news = "Breaking: Scientists discover revolutionary cure that doctors don't want you to know!"
    result = analyze_news(test_news)
    print("Analysis Result:")
    print(result["complete_response"])