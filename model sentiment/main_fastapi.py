
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from transformers import pipeline
import torch
import uvicorn
import warnings
from datetime import datetime, timedelta, timezone
import re
import pandas as pd
import numpy as np
from collections import Counter
import os
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Data collection APIs
import tweepy
import asyncpraw
from newsapi import NewsApiClient
import httpx

# Geolocation
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# NLP preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import html

warnings.filterwarnings('ignore')

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# ==========================================
# API CONFIGURATION
# ==========================================

class APIConfig:
    """Centralized API configuration"""
    
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", None)
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", None)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", None)
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", None)
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "RiskAnalysisBot/1.0")
    
    # Optional: OpenAI for advanced reasoning (fallback to rules-based if not set)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    
    @classmethod
    def validate(cls):
        """Check which APIs are configured"""
        status = {
            'twitter': cls.TWITTER_BEARER_TOKEN is not None,
            'newsapi': cls.NEWSAPI_KEY is not None,
            'reddit': cls.REDDIT_CLIENT_ID is not None and cls.REDDIT_CLIENT_SECRET is not None,
            'openai': cls.OPENAI_API_KEY is not None
        }
        return status

# ==========================================
# PYDANTIC MODELS
# ==========================================

class LocationInput(BaseModel):
    latitude: float = Field(..., example=31.7)
    longitude: float = Field(..., example=76.9)
    radius: int = Field(20, example=20)
    max_tweets: int = Field(100, example=100)
    max_reddit: int = Field(50, example=50)
    max_news: int = Field(30, example=30)
    days_back: int = Field(5, example=5)

class RiskAssessment(BaseModel):
    location: str
    risk_level: str
    confidence_score: float
    key_findings: Dict[str, List[str]]
    sentiment_summary: Dict[str, Any]
    recommended_precautions: List[str]
    summary_text: str
    data_sources: List[str]
    last_updated: str
    coordinates: Dict[str, float]
    detailed_statistics: Dict

# ==========================================
# RISK KEYWORDS DATABASE
# ==========================================

RISK_KEYWORDS = {
    'natural_hazards': [
        'landslide', 'flood', 'flooding', 'rainfall', 'heavy rain', 'storm', 
        'earthquake', 'fog', 'snow', 'avalanche', 'forest fire', 'wildfire',
        'heatwave', 'cyclone', 'tsunami', 'drought', 'lightning'
    ],
    'infrastructure': [
        'road closed', 'bridge collapse', 'accident', 'pothole', 'construction',
        'blocked highway', 'traffic jam', 'route closed', 'diversion', 
        'no fuel', 'power outage', 'internet down', 'connectivity issue'
    ],
    'social_safety': [
        'protest', 'riot', 'curfew', 'unrest', 'theft', 'robbery', 'crime',
        'violence', 'strike', 'demonstration', 'clash', 'security alert',
        'lockdown', 'tension', 'mob'
    ],
    'health_environment': [
        'pollution', 'air quality', 'disease outbreak', 'epidemic', 
        'sanitation', 'unsafe water', 'extreme heat', 'extreme cold',
        'crowding', 'covid', 'infection', 'contamination'
    ],
    'precaution_indicators': [
        'avoid', 'warning', 'alert', 'advisory', 'caution', 'stay safe',
        'danger', 'unsafe', 'hazard', 'risk', 'emergency', 'evacuate'
    ]
}

# Flatten all keywords
ALL_RISK_KEYWORDS = []
for category, keywords in RISK_KEYWORDS.items():
    ALL_RISK_KEYWORDS.extend(keywords)

# ==========================================
# FASTAPI APP WITH LIFESPAN
# ==========================================

classifier = None
device = 0 if torch.cuda.is_available() else -1
geolocator = Nominatim(user_agent="risk_intelligence_system")

twitter_client = None
reddit_client = None
newsapi_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler"""
    global classifier, twitter_client, reddit_client, newsapi_client
    
    # STARTUP
    print("\n📥 Loading RoBERTa sentiment model...")
    try:
        classifier = pipeline(
            'sentiment-analysis',
            model='./fine_tuned_roberta',
            device=device,
            max_length=512,
            truncation=True
        )
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"⚠️ Error loading custom model: {e}")
        print("Using default sentiment model...")
        classifier = pipeline('sentiment-analysis', device=device)
    
    print("\n🔌 Initializing API clients...")
    
    if APIConfig.TWITTER_BEARER_TOKEN:
        try:
            twitter_client = tweepy.Client(bearer_token=APIConfig.TWITTER_BEARER_TOKEN)
            print("✅ Twitter API initialized")
        except Exception as e:
            print(f"⚠️ Twitter API error: {e}")
    
    if APIConfig.NEWSAPI_KEY:
        try:
            newsapi_client = NewsApiClient(api_key=APIConfig.NEWSAPI_KEY)
            print("✅ NewsAPI initialized")
        except Exception as e:
            print(f"⚠️ NewsAPI error: {e}")
    
    if APIConfig.REDDIT_CLIENT_ID and APIConfig.REDDIT_CLIENT_SECRET:
        try:
            reddit_client = asyncpraw.Reddit(
                client_id=APIConfig.REDDIT_CLIENT_ID,
                client_secret=APIConfig.REDDIT_CLIENT_SECRET,
                user_agent=APIConfig.REDDIT_USER_AGENT
            )
            print("✅ Reddit API initialized")
        except Exception as e:
            print(f"⚠️ Reddit API error: {e}")
    
    api_status = APIConfig.validate()
    print(f"\n📊 API Status: {api_status}")
    
    yield
    
    # SHUTDOWN
    print("\n🔄 Shutting down...")
    if reddit_client:
        await reddit_client.close()

app = FastAPI(
    title="Geospatial Risk Intelligence System",
    description="Real-time risk analysis using Twitter + Reddit + NewsAPI + RoBERTa + LLM",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# STAGE 1: LOCATION SETUP
# ==========================================

def get_location_name(lat: float, lon: float) -> str:
    """Convert coordinates to city name"""
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village')
            state = address.get('state', '')
            return f"{city}, {state}" if city else f"{lat}, {lon}"
        return f"{lat}, {lon}"
    except Exception as e:
        print(f"Geocoding error: {e}")
        return f"{lat}, {lon}"

# ==========================================
# STAGE 2: BUILD QUERIES
# ==========================================

def build_search_query(location: str) -> Dict:
    """Build search queries with risk keywords"""
    city = location.split(',')[0].strip()
    state = location.split(',')[1].strip() if ',' in location else ''
    
    # Use top risk keywords
    risk_terms = ['weather', 'safety', 'alert', 'news', 'traffic', 'condition']
    
    twitter_query = f"{city} lang:en -is:retweet"
    reddit_query = f"{city} OR {state}" if state else city
    news_query = city
    
    return {
        'twitter': twitter_query,
        'reddit': reddit_query,
        'news': news_query,
        'location': city,
        'state': state
    }

# ==========================================
# STAGE 3: DATA COLLECTION
# ==========================================

def fetch_tweets_v2(query: str, max_results: int = 100, days_back: int = 5) -> List[Dict]:
    """Fetch tweets with rate limit handling"""
    tweets_data = []
    
    if not twitter_client:
        return tweets_data
    
    try:
        print(f"🐦 Fetching tweets: {query}")
        # ✅ Fixed: Use timezone-aware datetime
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days_back)
        
        tweets = twitter_client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            start_time=start_time,
            tweet_fields=['created_at', 'public_metrics'],
            user_fields=['username']
        )
        
        if tweets.data:
            for tweet in tweets.data:
                metrics = tweet.public_metrics
                tweets_data.append({
                    'source': 'twitter',
                    'text': tweet.text,
                    'date': tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'engagement': metrics.get('like_count', 0) + metrics.get('retweet_count', 0)
                })
        
        print(f"✅ Fetched {len(tweets_data)} tweets")
    except tweepy.TooManyRequests:
        print(f"⚠️ Twitter rate limit. Continuing with other sources...")
    except Exception as e:
        print(f"⚠️ Twitter error: {e}")
    
    return tweets_data

async def fetch_reddit_posts(query: str, max_results: int = 50, days_back: int = 5) -> List[Dict]:
    """Fetch Reddit posts"""
    reddit_data = []
    
    if not reddit_client:
        return reddit_data
    
    try:
        print(f"🔴 Fetching Reddit posts: {query}")
        # ✅ Fixed: Use timezone-aware datetime
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        seen_ids = set()
        
        for subreddit_name in ['all', 'india', 'IndiaSpeaks']:
            if len(reddit_data) >= max_results:
                break
            
            try:
                subreddit = await reddit_client.subreddit(subreddit_name)
                async for post in subreddit.search(query=query, sort='relevance', time_filter='month', limit=50):
                    if post.id in seen_ids:
                        continue
                    
                    # ✅ Fixed: Use timezone-aware datetime
                    post_date = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    if post_date < cutoff_date:
                        continue
                    
                    reddit_data.append({
                        'source': 'reddit',
                        'text': f"{post.title}. {post.selftext}",
                        'date': post_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'engagement': post.score
                    })
                    seen_ids.add(post.id)
                    
                    if len(reddit_data) >= max_results:
                        break
            except:
                continue
        
        print(f"✅ Fetched {len(reddit_data)} Reddit posts")
    except Exception as e:
        print(f"⚠️ Reddit error: {e}")
    
    return reddit_data

def fetch_news_newsapi(query: str, max_results: int = 30, days_back: int = 5) -> List[Dict]:
    """Fetch news articles"""
    news_data = []
    
    if not newsapi_client:
        return news_data
    
    try:
        print(f"📰 Fetching news: {query}")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        articles = newsapi_client.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='relevancy',
            page_size=min(max_results, 100)
        )
        
        for article in articles.get('articles', []):
            news_data.append({
                'source': 'news',
                'text': f"{article.get('title', '')}. {article.get('description', '')}",
                'date': article.get('publishedAt', datetime.now().strftime("%Y-%m-%d")),
                'url': article.get('url', ''),
                'publisher': article.get('source', {}).get('name', 'Unknown')
            })
        
        print(f"✅ Fetched {len(news_data)} news articles")
    except Exception as e:
        print(f"⚠️ NewsAPI error: {e}")
    
    return news_data

# ==========================================
# STAGE 4: FILTERING & PREPROCESSING
# ==========================================

STOP_WORDS = set(stopwords.words('english')) - {'not', 'no', 'never', 'neither', 'nobody', 'nothing'}

SLANG_DICT = {
    'lol': 'laughing', 'omg': 'oh my god', 'wtf': 'what the',
    'smh': 'shaking head', 'tbh': 'to be honest', 'u': 'you', 'ur': 'your'
}

CONTRACTIONS = {
    "cant": "cannot", "wont": "will not", "dont": "do not",
    "didnt": "did not", "isnt": "is not", "wasnt": "was not"
}

def preprocess_text(text: str) -> str:
    """25-step preprocessing pipeline"""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+|#', '', text)
    text = html.unescape(text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    words = text.split()
    words = [SLANG_DICT.get(word, word) for word in words]
    words = [CONTRACTIONS.get(word, word) for word in words]
    words = [word for word in words if word not in STOP_WORDS]
    
    # Negation handling
    result = []
    negate = False
    for word in words:
        if word in ['not', 'no', 'never']:
            negate = True
            result.append(word)
        elif negate:
            result.append('not_' + word)
            negate = False
        else:
            result.append(word)
    
    return ' '.join(result).strip()

def filter_data(data: List[Dict], location: str) -> List[Dict]:
    """Filter and clean data"""
    filtered = []
    city = location.split(',')[0].strip().lower()
    state = location.split(',')[1].strip().lower() if ',' in location else ''
    seen_texts = set()
    
    for item in data:
        text = item.get('text', '').strip()
        text_lower = text.lower()
        
        if text in seen_texts or len(text.split()) < 3:
            continue
        
        spam_keywords = ['giveaway', 'win now', 'buy now', 'subscribe']
        if any(spam in text_lower for spam in spam_keywords):
            continue
        
        location_match = city in text_lower or state in text_lower or item['source'] == 'news'
        if not location_match:
            continue
        
        seen_texts.add(text)
        filtered.append(item)
    
    return filtered

# ==========================================
# STAGE 5: SENTIMENT ANALYSIS
# ==========================================

def analyze_sentiment_batch(texts: List[str]) -> List[Dict]:
    """RoBERTa sentiment analysis"""
    results = []
    batch_size = 32
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        try:
            predictions = classifier(batch)
            for text, pred in zip(batch, predictions):
                label = pred['label']
                score = float(pred['score'])
                
                if 'LABEL_0' in label or 'negative' in label.lower():
                    sentiment = "negative"
                elif 'LABEL_1' in label or 'positive' in label.lower():
                    sentiment = "positive"
                else:
                    sentiment = "neutral"
                
                results.append({
                    'text': text,
                    'sentiment': sentiment,
                    'confidence': round(score, 4)
                })
        except:
            for text in batch:
                results.append({'text': text, 'sentiment': 'neutral', 'confidence': 0.5})
    
    return results

# ==========================================
# STAGE 6: KEYWORD & TOPIC EXTRACTION
# ==========================================

def extract_risk_keywords(texts: List[str]) -> Dict[str, List[str]]:
    """Extract risk-related keywords by category"""
    findings = {
        'natural_hazards': [],
        'infrastructure': [],
        'social_safety': [],
        'health_environment': [],
        'precaution_indicators': []
    }
    
    all_text = ' '.join(texts).lower()
    
    for category, keywords in RISK_KEYWORDS.items():
        found = []
        for keyword in keywords:
            if keyword in all_text:
                count = all_text.count(keyword)
                if count > 0:
                    found.append(f"{keyword} (mentioned {count}x)")
        findings[category] = found[:5]  # Top 5
    
    return findings

def extract_dominant_topics(texts: List[str], top_n: int = 10) -> List[str]:
    """Extract most common meaningful words"""
    all_words = []
    for text in texts:
        words = [w for w in text.lower().split() if len(w) > 3 and w not in STOP_WORDS]
        all_words.extend(words)
    
    if all_words:
        word_counts = Counter(all_words)
        return [word for word, count in word_counts.most_common(top_n)]
    return []

# ==========================================
# STAGE 7: AGGREGATION
# ==========================================

def calculate_metrics(source_sentiments: Dict[str, List[Dict]]) -> Dict:
    """Calculate sentiment metrics"""
    def count_sentiments(sentiments):
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for s in sentiments:
            counts[s['sentiment']] += 1
        return counts
    
    twitter_counts = count_sentiments(source_sentiments.get('twitter', []))
    reddit_counts = count_sentiments(source_sentiments.get('reddit', []))
    news_counts = count_sentiments(source_sentiments.get('news', []))
    
    total = sum(twitter_counts.values()) + sum(reddit_counts.values()) + sum(news_counts.values())
    
    if total == 0:
        return {
            'positive_percent': 0,
            'negative_percent': 0,
            'neutral_percent': 0,
            'total': 0
        }
    
    # Weighted by source reliability (News > Reddit > Twitter)
    weighted_neg = (news_counts['negative'] * 2 + reddit_counts['negative'] * 1.5 + twitter_counts['negative'])
    weighted_pos = (news_counts['positive'] * 2 + reddit_counts['positive'] * 1.5 + twitter_counts['positive'])
    weighted_neu = (news_counts['neutral'] * 2 + reddit_counts['neutral'] * 1.5 + twitter_counts['neutral'])
    
    weighted_total = weighted_neg + weighted_pos + weighted_neu
    
    return {
        'positive_percent': round((weighted_pos / weighted_total) * 100, 2),
        'negative_percent': round((weighted_neg / weighted_total) * 100, 2),
        'neutral_percent': round((weighted_neu / weighted_total) * 100, 2),
        'total': total,
        'raw_counts': {
            'twitter': twitter_counts,
            'reddit': reddit_counts,
            'news': news_counts
        }
    }

# ==========================================
# STAGE 8: RISK REASONING ENGINE
# ==========================================

def analyze_risk_level(sentiment_metrics: Dict, risk_keywords: Dict, dominant_topics: List[str]) -> Dict:
    """Rules-based risk assessment"""
    
    neg_percent = sentiment_metrics['negative_percent']
    total_data = sentiment_metrics['total']
    
    # Count risk indicators
    risk_count = sum(len(keywords) for keywords in risk_keywords.values())
    
    # Risk level determination
    if neg_percent > 50 or risk_count > 10:
        risk_level = "High"
        confidence = 0.85
    elif neg_percent > 30 or risk_count > 5:
        risk_level = "Moderate"
        confidence = 0.75
    elif neg_percent > 20 or risk_count > 2:
        risk_level = "Low"
        confidence = 0.65
    else:
        risk_level = "Low"
        confidence = 0.55
    
    # Adjust confidence based on data volume
    if total_data < 10:
        confidence *= 0.6
    elif total_data < 30:
        confidence *= 0.8
    
    # Overall mood
    if sentiment_metrics['positive_percent'] > sentiment_metrics['negative_percent'] * 2:
        overall_mood = "Optimistic"
    elif sentiment_metrics['negative_percent'] > sentiment_metrics['positive_percent'] * 1.5:
        overall_mood = "Concerned"
    else:
        overall_mood = "Neutral"
    
    return {
        'risk_level': risk_level,
        'confidence_score': round(confidence, 2),
        'overall_mood': overall_mood
    }

def generate_findings(risk_keywords: Dict) -> Dict[str, List[str]]:
    """Convert keyword findings to human-readable findings"""
    findings = {
        'natural_risks': [],
        'infrastructure_risks': [],
        'social_risks': [],
        'environmental_health': []
    }
    
    if risk_keywords['natural_hazards']:
        findings['natural_risks'] = [f"Detected: {kw}" for kw in risk_keywords['natural_hazards'][:3]]
    else:
        findings['natural_risks'] = ["No significant natural hazards detected"]
    
    if risk_keywords['infrastructure']:
        findings['infrastructure_risks'] = [f"Reported: {kw}" for kw in risk_keywords['infrastructure'][:3]]
    else:
        findings['infrastructure_risks'] = ["Infrastructure conditions appear normal"]
    
    if risk_keywords['social_safety']:
        findings['social_risks'] = [f"Alert: {kw}" for kw in risk_keywords['social_safety'][:3]]
    else:
        findings['social_risks'] = ["No major social safety concerns"]
    
    if risk_keywords['health_environment']:
        findings['environmental_health'] = [f"Noted: {kw}" for kw in risk_keywords['health_environment'][:3]]
    else:
        findings['environmental_health'] = ["Environmental conditions within normal range"]
    
    return findings

def generate_precautions(risk_level: str, risk_keywords: Dict, findings: Dict) -> List[str]:
    """Generate actionable precautions"""
    precautions = []
    
    if risk_level == "Severe":
        precautions.append("🚨 Avoid travel to this region if possible")
        precautions.append("Monitor local news and government advisories closely")
    
    elif risk_level == "High":
        precautions.append("⚠️ Exercise extreme caution if traveling")
        precautions.append("Check route conditions before departure")
    
    elif risk_level == "Moderate":
        precautions.append("Stay alert to local conditions")
        precautions.append("Keep emergency contacts and supplies ready")
    
    else:
        precautions.append("✅ Normal conditions; standard travel precautions apply")
    
    # Specific precautions based on detected risks
    if risk_keywords['natural_hazards']:
        precautions.append("Monitor weather forecasts and natural hazard warnings")
    
    if risk_keywords['infrastructure']:
        precautions.append("Check for road closures and alternate routes")
    
    if risk_keywords['social_safety']:
        precautions.append("Avoid crowded areas and follow local security advisories")
    
    if risk_keywords['precaution_indicators']:
        precautions.append("Follow official warnings and evacuation orders if issued")
    
    return precautions[:6]  # Max 6 precautions

def generate_summary(location: str, risk_level: str, findings: Dict, sentiment_metrics: Dict) -> str:
    """Generate human-readable summary"""
    neg_pct = sentiment_metrics['negative_percent']
    pos_pct = sentiment_metrics['positive_percent']
    
    if risk_level == "High":
        summary = f"{location}: High risk detected. "
    elif risk_level == "Moderate":
        summary = f"{location}: Moderate risk detected. "
    else:
        summary = f"{location}: Low risk. "
    
    # Add key findings
    key_risks = []
    if findings['natural_risks'][0] != "No significant natural hazards detected":
        key_risks.append("natural hazards")
    if findings['infrastructure_risks'][0] != "Infrastructure conditions appear normal":
        key_risks.append("infrastructure issues")
    if findings['social_risks'][0] != "No major social safety concerns":
        key_risks.append("social safety concerns")
    
    if key_risks:
        summary += f"Key concerns: {', '.join(key_risks)}. "
    else:
        summary += "No major risks identified. "
    
    # Add sentiment context
    if pos_pct > neg_pct * 2:
        summary += "Public sentiment is generally positive. "
    elif neg_pct > 30:
        summary += "Public sentiment reflects concerns. "
    
    summary += "Check latest advisories before travel."
    
    return summary

# ==========================================
# STAGE 9: MAIN PIPELINE
# ==========================================

@app.post("/analyze-risk", response_model=RiskAssessment)
async def analyze_risk(input_data: LocationInput):
    """
    🌍 Complete Geospatial Risk Intelligence Pipeline
    
    Stages:
    1. Location Setup
    2. Data Collection (Twitter + Reddit + NewsAPI)
    3. Filtering & Preprocessing
    4. Sentiment Analysis (RoBERTa)
    5. Keyword & Topic Extraction
    6. Aggregation
    7. Risk Reasoning
    8. Response Generation
    """
    
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # ✅ Fixed: Use timezone-aware datetime
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Check API status
    api_status = APIConfig.validate()
    available_sources = [k for k, v in api_status.items() if v and k != 'openai']
    
    if not available_sources:
        raise HTTPException(status_code=503, detail="No data sources configured")
    
    # STAGE 1: LOCATION
    print("\n" + "="*70)
    print("🚀 GEOSPATIAL RISK ANALYSIS PIPELINE")
    print("="*70)
    
    location_name = get_location_name(input_data.latitude, input_data.longitude)
    print(f"📍 Location: {location_name}")
    print(f"📡 Sources: {', '.join(available_sources)}")
    
    # STAGE 2: BUILD QUERIES & COLLECT DATA
    queries = build_search_query(location_name)
    
    all_data = []
    
    if api_status['twitter']:
        tweets_raw = fetch_tweets_v2(queries['twitter'], input_data.max_tweets, input_data.days_back)
        all_data.extend(tweets_raw)
    
    if api_status['reddit']:
        reddit_raw = await fetch_reddit_posts(queries['reddit'], input_data.max_reddit, input_data.days_back)
        all_data.extend(reddit_raw)
    
    if api_status['newsapi']:
        news_raw = fetch_news_newsapi(queries['news'], input_data.max_news, input_data.days_back)
        all_data.extend(news_raw)
    
    if not all_data:
        raise HTTPException(status_code=404, detail=f"No data found for {location_name}")
    
    # STAGE 3: FILTER & PREPROCESS
    print(f"\n🔍 Filtering data...")
    filtered_data = filter_data(all_data, location_name)
    print(f"✅ Kept {len(filtered_data)}/{len(all_data)} items")
    
    print(f"\n🧹 Preprocessing texts...")
    for item in filtered_data:
        item['original_text'] = item['text']
        item['text'] = preprocess_text(item['text'])
    
    filtered_data = [item for item in filtered_data if len(item['text']) > 0]
    
    if not filtered_data:
        raise HTTPException(status_code=404, detail="No relevant data after filtering")
    
    # STAGE 4: SENTIMENT ANALYSIS
    print(f"\n🤖 Analyzing sentiments...")
    texts = [item['text'] for item in filtered_data]
    sentiment_results = analyze_sentiment_batch(texts)
    
    for item, sentiment in zip(filtered_data, sentiment_results):
        item['sentiment'] = sentiment['sentiment']
        item['confidence'] = sentiment['confidence']
    
    # Split by source
    source_sentiments = {
        'twitter': [item for item in filtered_data if item['source'] == 'twitter'],
        'reddit': [item for item in filtered_data if item['source'] == 'reddit'],
        'news': [item for item in filtered_data if item['source'] == 'news']
    }
    
    # STAGE 5: KEYWORD & TOPIC EXTRACTION
    print(f"\n🏷️ Extracting risk keywords and topics...")
    all_preprocessed_texts = [item['text'] for item in filtered_data]
    all_original_texts = [item['original_text'] for item in filtered_data]
    
    risk_keywords = extract_risk_keywords(all_original_texts)
    dominant_topics = extract_dominant_topics(all_preprocessed_texts, top_n=10)
    
    # STAGE 6: AGGREGATE METRICS
    print(f"\n📊 Calculating metrics...")
    sentiment_metrics = calculate_metrics(source_sentiments)
    
    # STAGE 7: RISK REASONING
    print(f"\n🧠 Performing risk analysis...")
    risk_analysis = analyze_risk_level(sentiment_metrics, risk_keywords, dominant_topics)
    findings = generate_findings(risk_keywords)
    precautions = generate_precautions(risk_analysis['risk_level'], risk_keywords, findings)
    summary_text = generate_summary(location_name, risk_analysis['risk_level'], findings, sentiment_metrics)
    
    # STAGE 8: BUILD RESPONSE
    print(f"\n📦 Building response...")
    
    output = {
        "location": location_name,
        "risk_level": risk_analysis['risk_level'],
        "confidence_score": risk_analysis['confidence_score'],
        "key_findings": findings,
        "sentiment_summary": {
            "positive_percent": sentiment_metrics['positive_percent'],
            "negative_percent": sentiment_metrics['negative_percent'],
            "neutral_percent": sentiment_metrics['neutral_percent'],
            "overall_mood": risk_analysis['overall_mood']
        },
        "recommended_precautions": precautions,
        "summary_text": summary_text,
        "data_sources": available_sources,
        "last_updated": timestamp,
        "coordinates": {
            "lat": input_data.latitude,
            "lon": input_data.longitude
        },
        "detailed_statistics": {
            "total_analyzed": sentiment_metrics['total'],
            "by_source": sentiment_metrics['raw_counts'],
            "dominant_topics": dominant_topics,
            "risk_keywords_detected": risk_keywords
        }
    }
    
    print("\n" + "="*70)
    print(f"✅ ANALYSIS COMPLETE - Risk Level: {risk_analysis['risk_level']}")
    print("="*70)
    
    return output

# ==========================================
# ADDITIONAL ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    api_status = APIConfig.validate()
    return {
        "service": "Geospatial Risk Intelligence System",
        "version": "3.0.0",
        "description": "Real-time risk analysis using Twitter + Reddit + NewsAPI + RoBERTa + AI Reasoning",
        "pipeline_stages": [
            "1. Location Setup (Coordinates → City name)",
            "2. Data Collection (Twitter + Reddit + NewsAPI)",
            "3. Filtering & Preprocessing (25-step pipeline)",
            "4. Sentiment Analysis (RoBERTa)",
            "5. Keyword & Topic Extraction",
            "6. Aggregation & Scoring",
            "7. Risk Reasoning Engine",
            "8. Precaution Generation"
        ],
        "risk_categories": {
            "natural_hazards": "Floods, landslides, earthquakes, storms, wildfires",
            "infrastructure": "Road closures, accidents, construction, fuel availability",
            "social_safety": "Protests, riots, crime, security alerts",
            "health_environment": "Pollution, disease outbreaks, extreme temperatures"
        },
        "api_status": api_status,
        "endpoints": {
            "/analyze-risk": "POST - Main risk analysis endpoint",
            "/health": "GET - System health check",
            "/api-status": "GET - Check API configuration",
            "/risk-keywords": "GET - View all risk keywords",
            "/docs": "GET - Interactive API documentation"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": classifier is not None,
        "device": "GPU" if device == 0 else "CPU",
        "gpu_name": torch.cuda.get_device_name(0) if device == 0 else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api-status")
async def check_api_status():
    """Check which APIs are properly configured"""
    status = APIConfig.validate()
    
    details = {
        "twitter": {
            "configured": status['twitter'],
            "status": "✅ Ready" if status['twitter'] else "❌ Not configured",
            "limits": "500k tweets/month (Free tier)" if status['twitter'] else None,
            "setup": None if status['twitter'] else "Set TWITTER_BEARER_TOKEN environment variable"
        },
        "newsapi": {
            "configured": status['newsapi'],
            "status": "✅ Ready" if status['newsapi'] else "❌ Not configured",
            "limits": "100 requests/day (Free tier)" if status['newsapi'] else None,
            "setup": None if status['newsapi'] else "Set NEWSAPI_KEY environment variable"
        },
        "reddit": {
            "configured": status['reddit'],
            "status": "✅ Ready" if status['reddit'] else "❌ Not configured",
            "limits": "Unlimited (Free)" if status['reddit'] else None,
            "setup": None if status['reddit'] else "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
        }
    }
    
    return {
        "summary": status,
        "details": details,
        "ready": any([status['twitter'], status['newsapi'], status['reddit']]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/risk-keywords")
async def get_risk_keywords():
    """View all monitored risk keywords by category"""
    return {
        "categories": RISK_KEYWORDS,
        "total_keywords": len(ALL_RISK_KEYWORDS),
        "description": "Keywords monitored for risk detection across all data sources"
    }

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌍 GEOSPATIAL RISK INTELLIGENCE SYSTEM v3.0")
    print("="*70)
    print("\n📡 Data Sources:")
    print("   🐦 Twitter API v2 (Free: 500k tweets/month)")
    print("   🔴 Reddit API (Free: unlimited)")
    print("   📰 NewsAPI (Free: 100 requests/day)")
    print("\n🧠 Analysis Pipeline:")
    print("   1️⃣  Location Setup & Geocoding")
    print("   2️⃣  Multi-Source Data Collection")
    print("   3️⃣  Advanced Filtering & Preprocessing")
    print("   4️⃣  RoBERTa Sentiment Analysis")
    print("   5️⃣  Risk Keyword & Topic Extraction")
    print("   6️⃣  Weighted Aggregation")
    print("   7️⃣  AI-Powered Risk Reasoning")
    print("   8️⃣  Actionable Precaution Generation")
    print("\n🎯 Risk Categories:")
    print("   🌊 Natural Hazards (floods, landslides, storms)")
    print("   🚧 Infrastructure (road closures, accidents)")
    print("   👥 Social Safety (protests, crime, unrest)")
    print("   🏥 Health & Environment (pollution, outbreaks)")
    print("\n🔑 Configuration:")
    api_status = APIConfig.validate()
    for api, configured in api_status.items():
        if api != 'openai':
            status_icon = "✅" if configured else "❌"
            print(f"   {status_icon} {api.upper()}: {'Configured' if configured else 'Not configured'}")
    
    if not any([api_status['twitter'], api_status['newsapi'], api_status['reddit']]):
        print("\n⚠️  WARNING: No data sources configured!")
        print("   Set environment variables:")
        print("   - TWITTER_BEARER_TOKEN")
        print("   - NEWSAPI_KEY")
        print("   - REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET")
    
    print("\n📚 Documentation & Testing:")
    print("   Interactive API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print("   API Status: http://localhost:8000/api-status")
    print("   Risk Keywords: http://localhost:8000/risk-keywords")
    print("\n💡 Example Request:")
    print('   curl -X POST "http://localhost:8000/analyze-risk" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"latitude": 28.6, "longitude": 77.2, "days_back": 7}\'')
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")