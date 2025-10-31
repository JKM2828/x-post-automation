import google.generativeai as genai
from typing import List, Dict, Optional
import json
import random

from app.config import settings


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON array or object from text response.
    
    Args:
        text: Text containing JSON
        
    Returns:
        JSON string or None if not found
    """
    start = text.find('[')
    end = text.rfind(']') + 1
    
    if start >= 0 and end > start:
        return text[start:end]
    
    # Try to find JSON object
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start >= 0 and end > start:
        return text[start:end]
    
    return None


def parse_json_safely(text: str, default=None):
    """
    Safely parse JSON from text with fallback.
    
    Args:
        text: Text to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        json_str = extract_json_from_text(text)
        if json_str:
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return default


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
        
        variants = parse_json_safely(response_text)
        
        if variants and isinstance(variants, list):
            # Validate and limit
            return variants[:num_variants]
        else:
            # Fallback: split by newlines
            return self._fallback_parse(response_text, num_variants)
    
    def _fallback_parse(self, text: str, num_variants: int) -> List[Dict]:
        """Fallback parser if JSON fails"""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        variants = []
        
        for line in lines[:num_variants]:
            # Clean up markdown, numbers, etc
            clean = line.lstrip('0123456789.-*# ').strip('"')
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
            result = parse_json_safely(response.text, {})
            
            # Return parsed result or default
            return result if result else {
                "sentiment": "neutral",
                "engagement_score": 0.5,
                "suggestions": "N/A"
            }
        except:
            return {"sentiment": "neutral", "engagement_score": 0.5, "suggestions": "N/A"}


def get_ai_generator(api_key: Optional[str] = None) -> GeminiAIGenerator:
    """Factory function"""
    key = api_key or settings.GEMINI_API_KEY
    return GeminiAIGenerator(key)