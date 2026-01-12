@echo off
title Shifu Ecosystem Launcher
echo 🚀 Starting Shifu Ecosystem...
echo ---------------------------------------

:: 1. Start Streamlit in a new window
echo 📦 Starting Streamlit UI (Port 8501)...
start "Shifu UI" cmd /c "streamlit run app.py"

:: 2. Start API in another window
echo 🔌 Starting Shifu API (Port 8000)...
start "Shifu API" cmd /c "python api.py"

echo ---------------------------------------
echo ✅ Both servers are launching!
echo 🖥️  UI: http://localhost:8501
echo 📡 API: http://localhost:8000
echo ---------------------------------------
echo Close this window to keep them running, or close the specific windows to stop them.
pause
