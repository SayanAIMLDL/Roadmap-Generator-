# 🎓 Shifu AI: The Ultimate Learning Roadmap Architect

![Shifu Banner](https://img.shields.io/badge/Shifu-AI--Powered--Learning-blue?style=for-the-badge&logo=openai)
![Status](https://img.shields.io/badge/Status-Live--Ready-brightgreen?style=for-the-badge)

**Shifu** is a production-grade educational platform designed to generate comprehensive, end-to-end learning roadmaps. Using advanced RAG (Retrieval-Augmented Generation) and the power of Groq's high-speed Llama models, Shifu breaks down complex subjects into digestible modules, provides verified learning resources, and offers an interactive UI to visualize your journey.

---

## 🚀 Key Features

*   **🎯 Zero-Gap Learning Path**: Generates roadmaps up to 5 levels deep, ensuring you never miss a foundational or expert concept.
*   **🤖 Expert Persona**: Powered by "Dr. Shifu," an AI persona optimized for educational architecture and pedagogical design.
*   **🔗 Verified Resources**: Automatically fetches high-quality learning links from Wikipedia and provides smart search fallbacks for Medium and Google.
*   **💻 Developer-First API**: Includes a high-performance **FastAPI** backend for seamless integration with external websites and mobile apps.
*   **✨ Premium UI**: Beautiful, interactive Streamlit interface with real-time Markmap visualizations.
*   **🛡️ Production Security**: Robust input validation, prompt injection protection, and rate limiting out of the box.

---

## 🏛️ Architecture

Shifu operates as a dual-layer ecosystem:

1.  **Frontend (UI)**: Built with Streamlit for a fast, interactive experience.
2.  **Backend (API)**: Built with FastAPI for external developers to plug Shifu's power into their own products.
3.  **RAG Engine**: Uses FAISS vector store and HuggingFace embeddings to retrieve expert knowledge from curated sources.

---

## 🛠️ Quick Start

### 1. Installation
Ensure you have Python 3.9+ installed.

```bash
# Clone the repository
git clone https://github.com/SayanAIMLDL/Shifu.git
cd Shifu

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your keys:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Launching
We've made it easy with a one-click launcher for Windows:
*   Simply double-click **`start_shifu.bat`** to launch both the UI and the API simultaneously.

Alternatively, launch them manually:
```bash
# Start the UI
streamlit run app.py

# Start the API (in a separate terminal)
python api.py
```

---

## 📡 API Integration

Integrating Shifu with your own website is easy. Check out the [API Integration Guide](./API_INTEGRATION_GUIDE.md) for full details.

**Simple JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/api/roadmap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'Machine Learning' })
});
const roadmap = await response.json();
console.log(roadmap.data.roadmap);
```

---

## 📂 Project Structure

*   `app.py`: Streamlit entry point.
*   `api.py`: FastAPI server implementation.
*   `roadmap_generator.py`: Core logic for roadmap hierarchy.
*   `content_generator.py`: Detailed topic content and link generator.
*   `rag_engine.py`: Knowledge retrieval and LLM setup.
*   `security.py`: Validation and threat protection.
*   `start_shifu.bat`: Automation script for Windows users.

---

## 👤 Author

**Sayan**  
GitHub: [@SayanAIMLDL](https://github.com/SayanAIMLDL)

---

## 📜 License

This project is for educational purposes. All educational content generated is intended for personal learning and development.
