"""
Configuration Management for Shifu AI
Secure configuration with environment variable validation
"""
import os
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration management with validation"""
    
    def __init__(self):
        load_dotenv()
        self._validate_required_keys()
    
    def _validate_required_keys(self):
        """Validate that all required environment variables are present"""
        required_keys = ['GROQ_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            error_msg = f"Missing required environment variables: {missing_keys}"
            logger.critical(error_msg)
            raise ValueError(error_msg)
    
    @property
    def groq_api_key(self) -> str:
        """Get Groq API key from environment"""
        key = os.getenv('GROQ_API_KEY')
        if not key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return key
    
    @property
    def groq_model(self) -> str:
        """Get Groq model name"""
        return os.getenv('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
    
    @property
    def knowledge_base_file(self) -> str:
        """Get knowledge base file path"""
        return os.getenv('KNOWLEDGE_BASE_FILE', 'knowledge_base.txt')
    
    @property
    def vector_db_path(self) -> str:
        """Get vector database path"""
        return os.getenv('VECTOR_DB_PATH', 'faiss_index_hf')
    
    @property
    def roadmap_data_dir(self) -> str:
        """Get roadmap data directory"""
        return os.getenv('ROADMAP_DATA_DIR', 'roadmap_data')
    
    @property
    def log_level(self) -> str:
        """Get logging level"""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts for API calls"""
        return int(os.getenv('MAX_RETRIES', '3'))
    
    @property
    def rate_limit_delay(self) -> float:
        """Get rate limit delay in seconds"""
        return float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
    
    @property
    def request_timeout(self) -> int:
        """Get request timeout in seconds"""
        return int(os.getenv('REQUEST_TIMEOUT', '30'))

# Global configuration instance
config = Config()
