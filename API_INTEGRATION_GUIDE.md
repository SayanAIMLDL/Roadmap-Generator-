# Shifu API Integration Guide

## 🚀 Quick Start

### Step 1: Install API Dependencies
```bash
pip install fastapi uvicorn pydantic
```

### Step 2: Start the API Server
```bash
python api.py
```

The API will be available at:
- **API Endpoint**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

---

## 📡 API Endpoints

### 1. Generate Roadmap
**Endpoint**: `POST /api/roadmap`

**Request**:
```json
{
  "query": "Learn Python programming",
  "context": "I'm a complete beginner"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "query": "Learn Python programming",
    "roadmap": {
      "title": "Complete Python Mastery Roadmap",
      "modules": [...]
    }
  }
}
```

### 2. Generate Content
**Endpoint**: `POST /api/content`

**Request**:
```json
{
  "topic": "Python Variables",
  "context": "beginner level"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "description": "...",
    "key_points": [...],
    "code_snippet": "...",
    "links": [...]
  }
}
```

---

## 🌐 Integration with Your Friend's Website

### Method 1: JavaScript Fetch API

```html
<script>
async function getShifuRoadmap(topic) {
    const response = await fetch('http://localhost:8000/api/roadmap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: topic,
            context: "beginner"
        })
    });
    
    const data = await response.json();
    console.log(data.data.roadmap);
}

// Usage
getShifuRoadmap("Machine Learning");
</script>
```

### Method 2: jQuery

```javascript
$.ajax({
    url: 'http://localhost:8000/api/roadmap',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        query: 'Web Development',
        context: 'I know HTML/CSS'
    }),
    success: function(response) {
        console.log(response.data.roadmap);
    }
});
```

### Method 3: React

```jsx
import React, { useState } from 'react';

function ShifuIntegration() {
    const [roadmap, setRoadmap] = useState(null);
    
    const generateRoadmap = async (topic) => {
        const response = await fetch('http://localhost:8000/api/roadmap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: topic })
        });
        
        const data = await response.json();
        setRoadmap(data.data.roadmap);
    };
    
    return (
        <div>
            <button onClick={() => generateRoadmap('Python')}>
                Generate Roadmap
            </button>
            {roadmap && <div>{roadmap.title}</div>}
        </div>
    );
}
```

---

## 🔒 Production Deployment

### 1. Update CORS Settings
In `api.py`, change:
```python
allow_origins=["*"]  # Development
```
To:
```python
allow_origins=["https://your-friend-website.com"]  # Production
```

### 2. Deploy Options

**Option A: Deploy on Same Server**
```bash
# Run API on port 8000
python api.py
```

**Option B: Deploy on Cloud (Heroku/Railway/Render)**
```bash
# Add Procfile
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Option C: Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "api.py"]
```

---

## 📝 Example Integration

I've created `integration_example.html` - open it in a browser to see a working demo!

**To test:**
1. Start API: `python api.py`
2. Open: `integration_example.html` in browser
3. Enter a topic and click "Generate Roadmap"

---

## 🔧 Troubleshooting

**CORS Error?**
- Make sure `allow_origins` includes your friend's domain
- Check browser console for errors

**Connection Refused?**
- Ensure API is running: `python api.py`
- Check firewall settings

**Slow Response?**
- First request is slow (AI model loading)
- Subsequent requests are faster

---

## 📞 Support

For issues, check:
- API Docs: http://localhost:8000/docs
- Logs: Check terminal where `python api.py` is running
