"""Content Generator - AI-powered educational content creation with caching."""

import json
import os
import hashlib
import threading
import requests
import random
import time
from typing import Dict, List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from config import config
from logger_config import shifu_logger
from security import SecurityValidator, RateLimiter


class ContentGenerator:
    """Generates educational content for topics using LLM with smart caching."""

    def __init__(self, llm: ChatGroq, data_dir: str = None):
        self.llm = llm
        self.data_dir = data_dir or config.roadmap_data_dir
        self.cache_dir = os.path.join(self.data_dir, "content_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.rate_limiter = RateLimiter(max_requests=30, time_window=60)
        self.headers = {
            'User-Agent': 'ShifuEduBot/1.0 (Educational AI by Sayan; +https://github.com/SayanAIMLDL)',
            'Accept': 'application/json'
        }
        self._lock = threading.Lock()
        shifu_logger.info(f"ContentGenerator initialized with cache dir: {self.cache_dir}")

    def generate_topic_content(self, topic_name: str, context: str = "") -> Dict:
        """Generate comprehensive content for a topic with description, examples, and links."""
        try:
            validated_topic = SecurityValidator.validate_topic(topic_name)
            validated_context = SecurityValidator.validate_context(context)
            
            cache_key = f"{validated_topic}_{validated_context}"
            cached = self._load_from_cache(cache_key)
            
            if cached:
                if not cached.get("links"):
                    cached["links"] = self.generate_verified_links(cached.get("search_key", validated_topic))
                    self._save_to_cache(cache_key, cached)
                return cached

            shifu_logger.info(f"Generating content: {validated_topic}")
            
            prompt = PromptTemplate(
                template="""You are Dr. Shifu, a world-renowned educational architect and learning scientist with 20+ years of experience designing personalized learning paths. You specialize in breaking down complex topics into digestible, actionable steps.

Your mission: Create a comprehensive, beginner-friendly learning module that empowers students to master the topic quickly and confidently.

TOPIC TO TEACH: {topic}
LEARNER'S BACKGROUND: {context}

INSTRUCTIONS:
1. Analyze the learner's background and adapt your explanation accordingly
2. Use real-world analogies and practical examples
3. Include actionable code examples (if applicable)
4. Provide clear next steps for continued learning
5. Return ONLY valid JSON - no extra text

OUTPUT FORMAT (strict JSON):
{{
  "description": "Start with 'Imagine...' or 'Think of...' to create a relatable analogy, then explain the concept clearly in 120-150 words. Focus on WHY it matters and HOW it's used in real-world scenarios.",
  "key_points": [
    "Core concept 1 with practical application",
    "Core concept 2 with real-world example", 
    "Core concept 3 with actionable insight",
    "Common pitfall or best practice"
  ],
  "code_snippet": "Provide a simple, well-commented code example that demonstrates the concept. Use realistic variable names and include inline comments explaining each step. If not applicable to coding, write 'N/A'.",
  "search_key": "Optimized search query to find the best learning resources (be specific, e.g., 'Python list comprehension tutorial' not just 'Python')",
  "next_steps": "Suggest 2-3 specific follow-up topics or skills to learn next, explaining how they build upon this foundation."
}}

REMEMBER: You're teaching a real person who wants to learn efficiently. Make it engaging, practical, and actionable!""",
                input_variables=["topic", "context"]
            )
            
            response = self.llm.invoke(prompt.format(topic=validated_topic, context=validated_context), max_tokens=800)
            content = self._extract_json(response.content if hasattr(response, 'content') else str(response))
            
            if not content:
                content = self._fallback_content(validated_topic)
            
            if 'code_snippet' in content:
                content['code_snippet'] = content['code_snippet'].replace("<script", " ")
                
            content["links"] = self.generate_verified_links(content.get("search_key", validated_topic))
            self._save_to_cache(cache_key, content)
            return content

        except Exception as e:
            shifu_logger.error(f"Content generation failed: {topic_name}", exception=e)
            return self._fallback_content(topic_name)

    def generate_verified_links(self, search_query: str) -> List[Dict]:
        """Find educational resources from Wikipedia with fallback search links."""
        try:
            query = SecurityValidator.validate_query(search_query)
            links = []
            
            # Fetch from Wikipedia (free, no API key needed)
            wiki = self._fetch_wikipedia(query)
            if wiki:
                links.append(wiki)

            # Add fallback search links
            links.append({
                "title": f"Medium: {query}",
                "url": f"https://medium.com/search?q={query.replace(' ', '+')}",
                "source": "Medium"
            })
            links.append({
                "title": f"Google: {query}",
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "source": "Google"
            })

            return links[:5]
        except Exception as e:
            shifu_logger.warning(f"Link generation failed: {e}")
            return []

    def _fetch_wikipedia(self, query: str) -> Optional[Dict]:
        """Fetch article from Wikipedia OpenSearch API."""
        try:
            self._rate_limit()
            url = "https://en.wikipedia.org/w/api.php"
            params = {"action": "opensearch", "search": query, "limit": 1, "format": "json"}
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 3 and data[1] and data[3]:
                    return {"title": f"Wikipedia: {data[1][0]}", "url": data[3][0], "source": "Wikipedia"}
        except:
            pass
        return None

    def _rate_limit(self):
        """Apply rate limiting with random delay."""
        if not self.rate_limiter.is_allowed():
            time.sleep(self.rate_limiter.get_wait_time())
        time.sleep(random.uniform(0.1, 0.3))

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response text."""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        return None

    def _fallback_content(self, topic: str) -> Dict:
        """Return basic content when generation fails."""
        return {
            "description": f"Overview of {topic}.",
            "key_points": [topic],
            "code_snippet": "N/A",
            "links": [],
            "next_steps": "Continue learning"
        }

    def _save_to_cache(self, key: str, content: Dict):
        """Save content to cache file."""
        try:
            h = hashlib.md5(key.encode()).hexdigest()
            with open(os.path.join(self.cache_dir, f"{h}.json"), "w", encoding='utf-8') as f:
                json.dump(content, f, indent=2)
        except:
            pass

    def _load_from_cache(self, key: str) -> Optional[Dict]:
        """Load content from cache file."""
        try:
            h = hashlib.md5(key.encode()).hexdigest()
            path = os.path.join(self.cache_dir, f"{h}.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return None
