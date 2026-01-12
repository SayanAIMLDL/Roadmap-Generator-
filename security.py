"""
Security utilities for Shifu AI
Input validation, sanitization, and security measures against Prompt Engineering threats.
"""
import re
import html
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SecurityValidator:
    """
    Advanced Security Guard against:
    - Prompt Injection (Direct/Indirect)
    - Jailbreaking (Roleplay/Hypotheticals)
    - Prompt Leaking
    - Obfuscation
    """
    
    # 1. Allow general safe chars, but we will rely more on Pattern matching for threats
    SAFE_INPUT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.\,\?\!\-\_\(\)\[\]\{\}\/\:\;\@\$\'\"]+$')
    
    # 2. Strict Length Limits (Mitigates Buffer Overflow / Token exhaustion)
    MAX_QUERY_LENGTH = 1000
    MAX_CONTEXT_LENGTH = 2000
    MAX_TOPIC_LENGTH = 200
    
    # 3. PATTERN BLOCKLIST (The Core Defense)
    # These regexes catch specific injection attempts defined in your threat model
    INJECTION_PATTERNS = [
        # Override Commands (Prompt Injection)
        r'\b(ignore|forget|disregard|drop)\s+(all\s+)?(previous|prior|above|preceding)\s+(instructions|commands|prompts|rules)',
        r'\b(override|bypass|ignore)\s+(system|safety)\s+(filters|guardrails)',
        
        # Leaking Instructions (Prompt Leaking)
        r'(repeat|output|print|show|reveal|display|copy)\s+(the\s+)?(full\s+)?(initial|system|internal)\s+(prompt|instructions|rules)',
        r'what\s+are\s+your\s+(instructions|rules|hidden\s+prompts)',
        
        # Roleplaying / Jailbreaking
        r'\b(act|behave|roleplay|pretend)\s+as\s+(?!an\s+expert\s+educator)', # Allow 'expert educator', block others (DAN, unrestricted modes)
        r'\b(you\s+are\s+now|from\s+now\s+on)\s+(?!Shifu)', # Prevent Identity shifting
        r'\b(DAN|DA|jailbreak|unfiltered|god\s+mode)\b',
        
        # Obfuscation / Encoding indicators
        r'(base64|rot13|hex|ascii)\s+(decode|encoded)',
        
        # Code Injection / XSS
        r'<script', 
        r'javascript:', 
        r'vbscript:',
        r'onload=', 
        r'onerror=',
        
        # System delimiters (prevent closing tags if using XML tagging)
        r'```', 
        r'---',
        r'<user_input>', 
        r'</user_input>'
    ]
    
    @classmethod
    def scan_for_threats(cls, text: str) -> Tuple[bool, str]:
        """
        Scans text for malicious patterns.
        Returns: (is_safe, reason)
        """
        if not text:
            return True, ""
            
        # Check 1: Length (Denial of Service mitigation)
        if len(text) > cls.MAX_CONTEXT_LENGTH + 500: # Slight buffer
            return False, "Input length exceeds safety limits"

        # Check 2: Pattern Matching (Injection/Jailbreak)
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return False, f"Potential injection pattern detected: {pattern[:20]}..."

        # Check 3: High Entropy / Obfuscation (Simple check for Base64 blocks)
        # Looks for words longer than 50 chars with no spaces (indicates encoded payload)
        long_strings = re.findall(r'\S{50,}', text)
        if long_strings:
            return False, "Input contains suspicious long strings (possible obfuscation)"

        return True, "Safe"

    @classmethod
    def sanitize_input(cls, text: str, max_length: int = 1000) -> str:
        """
        Sanitizes input by removing dangerous characters and neutralizing logic.
        """
        if not isinstance(text, str):
            return ""

        # 1. Truncate
        text = text[:max_length]
        
        # 2. Block Logic
        is_safe, reason = cls.scan_for_threats(text)
        if not is_safe:
            logger.warning(f"Threat Blocked: {reason} | Input: {text[:50]}...")
            # We do NOT allow the unsafe text to proceed. 
            # We return a generic safe topic or raise error depending on strategy.
            # Here we sanitize effectively by removing match or stripping.
            # Ideally: Throw error.
            raise ValueError("Your input was flagged by our security filter. Please try a valid learning topic.")

        # 3. HTML Escape (XSS defense)
        text = html.escape(text)
        
        # 4. Remove System Delimiters (Prevent XML Tag spoofing in prompt)
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        
        # 5. Normalization
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def validate_query(cls, query: str) -> str:
        """Validate query specifically for learning"""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Scan for injection logic first
        return cls.sanitize_input(query, cls.MAX_QUERY_LENGTH)

    @classmethod
    def validate_context(cls, context: str) -> str:
        """Validate context"""
        if not context:
            return ""
        return cls.sanitize_input(context, cls.MAX_CONTEXT_LENGTH)

    @classmethod
    def validate_topic(cls, topic: str) -> str:
        return cls.sanitize_input(topic, cls.MAX_TOPIC_LENGTH)

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Check for malicious URLs (Javascript URI, Phishing)"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            # Prevent JS execution via URL
            if "javascript:" in url.lower() or "data:" in url.lower():
                return False
            return True
        except:
            return False

    @classmethod
    def validate_json_structure(cls, data: Dict, required_keys: List[str]) -> bool:
        if not isinstance(data, dict):
            return False
        return all(key in data for key in required_keys)
        
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        filename = re.sub(r'[<>:"|?*]', '', filename)
        return filename[:255].strip()

class RateLimiter:
    """Sliding window rate limiting algorithm"""
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def is_allowed(self) -> bool:
        """Check if request is allowed by the rate limit"""
        current_time = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        return False

    def get_wait_time(self) -> float:
        """Calculate wait time until next request is allowed"""
        if not self.requests:
            return 0.1
        current_time = time.time()
        oldest_request = self.requests[0]
        wait_time = self.time_window - (current_time - oldest_request)
        return max(0.1, wait_time)