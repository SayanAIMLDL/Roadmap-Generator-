"""
FastAPI REST API for Shifu
Allows external websites to integrate with Shifu's roadmap generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn

from rag_engine import load_llm
from roadmap_generator import RoadmapGenerator
from content_generator import ContentGenerator
from logger_config import shifu_logger

# Initialize FastAPI
app = FastAPI(
    title="Shifu API",
    description="AI-powered learning roadmap generation API",
    version="1.0.0"
)

# Enable CORS (allow your friend's website to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your friend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM and generators
llm = load_llm()
roadmap_gen = RoadmapGenerator(llm)
content_gen = ContentGenerator(llm)

# Request/Response Models
class RoadmapRequest(BaseModel):
    query: str
    context: Optional[str] = ""

class ContentRequest(BaseModel):
    topic: str
    context: Optional[str] = ""

class RoadmapResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

class ContentResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None


# API Endpoints
@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Shifu API is running!",
        "version": "1.0.0",
        "endpoints": {
            "generate_roadmap": "/api/roadmap",
            "generate_content": "/api/content",
            "docs": "/docs"
        }
    }

@app.post("/api/roadmap", response_model=RoadmapResponse)
def generate_roadmap(request: RoadmapRequest):
    """
    Generate a comprehensive learning roadmap
    
    Example:
    POST /api/roadmap
    {
        "query": "Learn Python programming",
        "context": "I'm a complete beginner"
    }
    """
    try:
        shifu_logger.info(f"API: Generating roadmap for: {request.query}")
        
        roadmap_data = roadmap_gen.generate_roadmap_structure(
            query=request.query,
            user_context=request.context
        )
        
        return RoadmapResponse(
            success=True,
            data=roadmap_data
        )
    except Exception as e:
        shifu_logger.error(f"API: Roadmap generation failed", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content", response_model=ContentResponse)
def generate_content(request: ContentRequest):
    """
    Generate detailed content for a specific topic
    
    Example:
    POST /api/content
    {
        "topic": "Python Variables",
        "context": "beginner level"
    }
    """
    try:
        shifu_logger.info(f"API: Generating content for: {request.topic}")
        
        content_data = content_gen.generate_topic_content(
            topic_name=request.topic,
            context=request.context
        )
        
        return ContentResponse(
            success=True,
            data=content_data
        )
    except Exception as e:
        shifu_logger.error(f"API: Content generation failed", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/roadmap/{roadmap_id}")
def get_roadmap(roadmap_id: str):
    """Load existing roadmap by ID"""
    try:
        filename = f"roadmap_{roadmap_id}.json"
        roadmap_data = roadmap_gen.load_roadmap(filename)
        
        if roadmap_data:
            return RoadmapResponse(success=True, data=roadmap_data)
        else:
            raise HTTPException(status_code=404, detail="Roadmap not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting Shifu API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 API Endpoint: http://localhost:8000/api/roadmap")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
