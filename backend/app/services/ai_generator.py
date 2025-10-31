import google.generativeai as genai
from typing import List, Dict, Optional
import json
import random

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
        variant_count: int = 3,
        include_hashtags: bool = True,
        include_call_to_action: bool = True
    ) -> List[Dict]:
        """
        Generate multiple tweet variants using Gemini
        
        Args:
            topic: Main topic/theme
            tone: professional, casual, humorous, inspirational
            variant_count: Number of variants (1-5)
            include_hashtags: Add relevant hashtags
            include_call_to_action: Add call-to-action
            
        Returns:
            List of dicts with 'text' and 'viral_score'
        """
        
        prompt = self._build_prompt(topic, tone, variant_count, include_hashtags, include_call_to_action)
        
        try:
            response = self.model.generate_content(prompt)
            variants = self._parse_response(response.text, variant_count)
            return variants
        except Exception as gemini_error:
            raise Exception(f"Gemini API error: {str(gemini_error)}")
    
    def _build_prompt(
        self, 
        topic: str, 
        tone: str, 
        variant_count: int,
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> str:
        """Build optimized prompt for Gemini"""
        
        prompt = f"""You are a viral tweet expert. Generate {variant_count} unique tweets about: {topic}

Requirements:
- Tone: {tone}
- Max 280 characters each
- {'Include 2-3 relevant hashtags' if include_hashtags else 'No hashtags'}
- {'Include engaging call-to-action' if include_call_to_action else 'No call-to-action'}
- Make them engaging and shareable
- Use emojis strategically

Format response as JSON array:
[
  {{"text": "tweet text here", "viral_score": 0.85}},
  {{"text": "tweet text here", "viral_score": 0.78}}
]

Viral score = predicted engagement potential (0-1)"""
        
        return prompt
    
    def _parse_response(self, response_text: str, variant_count: int) -> List[Dict]:
        """Parse Gemini response and extract tweets"""
        
        try:
            # Try to extract JSON from response
            json_start_index = response_text.find('[')
            json_end_index = response_text.rfind(']') + 1
            
            if json_start_index >= 0 and json_end_index > json_start_index:
                json_string = response_text[json_start_index:json_end_index]
                variants = json.loads(json_string)
                
                # Validate and limit
                return variants[:variant_count]
            else:
                # Fallback: split by newlines
                return self._fallback_parse(response_text, variant_count)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response_text, variant_count)
    
    def _fallback_parse(self, text: str, variant_count: int) -> List[Dict]:
        """Fallback parser if JSON fails"""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        variants = []
        
        for line in lines[:variant_count]:
            # Clean up markdown, numbers, etc
            cleaned_line = line.lstrip('0123456789.-*# ').strip('"')
            if len(cleaned_line) > 10 and len(cleaned_line) <= 280:
                variants.append({
                    'text': cleaned_line,
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
        except Exception as analysis_error:
            return {"sentiment": "neutral", "engagement_score": 0.5, "suggestions": "N/A"}


def get_ai_generator(api_key: Optional[str] = None) -> GeminiAIGenerator:
    """Factory function"""
    api_key_to_use = api_key or settings.GEMINI_API_KEY
    return GeminiAIGenerator(api_key_to_use)