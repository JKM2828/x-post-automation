import google.generativeai as genai
from typing import List, Dict, Optional
import json
import random
from functools import lru_cache

from app.config import settings


class GeminiAIGenerator:
    """
    AI content generator using Google Gemini API
    Free tier: 15 requests per minute, 1500 per day
    Much cheaper than OpenAI GPT-4
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_tweet_variants(
        self,
        topic: str,
        tone: str = "professional",
        num_variants: int = 3,
        include_hashtags: bool = True,
        include_cta: bool = True
    ) -> List[Dict]:
        """
        Generate multiple tweet variants using Gemini
        
        Args:
            topic: Main topic/theme
            tone: professional, casual, humorous, inspirational
            num_variants: Number of variants (1-5)
            include_hashtags: Add relevant hashtags
            include_cta: Add call-to-action
            
        Returns:
            List of dicts with 'text' and 'viral_score'
        """
        
        prompt = self._build_prompt(topic, tone, num_variants, include_hashtags, include_cta)
        
        try:
            response = self.model.generate_content(prompt)
            variants = self._parse_response(response.text, num_variants)
            return variants
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _build_prompt(
        self, 
        topic: str, 
        tone: str, 
        num_variants: int,
        include_hashtags: bool,
        include_cta: bool
    ) -> str:
        """Build optimized prompt for Gemini"""
        
        prompt = f"""You are a viral tweet expert. Generate {num_variants} unique tweets about: {topic}

Requirements:
- Tone: {tone}
- Max 280 characters each
- {'Include 2-3 relevant hashtags' if include_hashtags else 'No hashtags'}
- {'Include engaging call-to-action' if include_cta else 'No call-to-action'}
- Make them engaging and shareable
- Use emojis strategically

Format response as JSON array:
[
  {{"text": "tweet text here", "viral_score": 0.85}},
  {{"text": "tweet text here", "viral_score": 0.78}}
]

Viral score = predicted engagement potential (0-1)"""
        
        return prompt
    
    def _parse_response(self, response_text: str, num_variants: int) -> List[Dict]:
        """Parse Gemini response and extract tweets"""
        
        try:
            # Try to extract JSON from response (optimized search)
            start = response_text.find('[')
            end = response_text.rfind(']')
            
            if start >= 0 and end > start:
                json_str = response_text[start:end + 1]
                variants = json.loads(json_str)
                
                # Validate and limit
                return variants[:num_variants]
            else:
                # Fallback: split by newlines
                return self._fallback_parse(response_text, num_variants)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response_text, num_variants)
    
    def _fallback_parse(self, text: str, num_variants: int) -> List[Dict]:
        """Fallback parser if JSON fails"""
        
        # Pre-compile stripping characters for efficiency
        strip_chars = '0123456789.-*# "'
        variants = []
        
        # Split and filter lines in one pass
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines[:num_variants]:
            # Clean up markdown, numbers, etc
            clean = line.lstrip(strip_chars).rstrip('"')
            if len(clean) > 10 and len(clean) <= 280:
                variants.append({
                    'text': clean,
                    'viral_score': round(random.uniform(0.6, 0.9), 2)
                })
        
        return variants if variants else [{'text': 'Failed to generate', 'viral_score': 0.0}]
    
    def analyze_tweet_sentiment(self, text: str) -> Dict:
        """Analyze sentiment and engagement potential"""
        
        prompt = f"""Analyze this tweet and provide sentiment score:

Tweet: {text}

Respond with JSON:
{{"sentiment": "positive/negative/neutral", "engagement_score": 0.75, "suggestions": "brief tip"}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return {"sentiment": "neutral", "engagement_score": 0.5, "suggestions": "N/A"}


@lru_cache(maxsize=128)
def get_ai_generator(api_key: Optional[str] = None) -> GeminiAIGenerator:
    """Factory function with caching to avoid repeated initialization
    
    Caches up to 128 different API key configurations to handle multiple users efficiently
    """
    key = api_key or settings.GEMINI_API_KEY
    return GeminiAIGenerator(key)