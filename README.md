# LLM Chatbot Service

A minimal but production-oriented chatbot service built with FastAPI, LangChain, and LangGraph. Demonstrates MLOps fundamentals, DAG-based routing, and multi-user session management.

## Features

- **LLM Integration**: Google Gemini API via LangChain
- **Intelligent Routing**: LangGraph DAG routes to calculator or LLM based on input
- **Multi-User Support**: Session-based memory per user (in-memory storage)
- **Conversation Memory**: ConversationBufferMemory persists context within sessions
- **Monitoring**: Tracks request latency and throughput
- **Logging**: Per-module file-based logging
- **Docker Ready**: Containerized deployment

## Live Deployment

This project is fully deployed using free-tier cloud infrastructure for demonstration and testing.

### Frontend (GitHub Pages)
Static HTML and JavaScript frontend deployed on GitHub Pages.

Live URL:
https://shivamsonawane2003.github.io/MLOps_task/

---

### Backend (Render – Free Plan)
FastAPI backend deployed using Docker on Render’s free tier.

Base URL:
https://mlops-task-jrvu.onrender.com

API Documentation (Swagger):
https://mlops-task-jrvu.onrender.com/docs

Health Check:
https://mlops-task-jrvu.onrender.com/health

---

### Deployed Architecture

Browser (GitHub Pages)
        |
        | HTTPS (POST /chat)
        v
FastAPI Backend (Render)
        |
        | LangGraph Router
        |-- Calculator Node
        |-- Gemini LLM Node

---

### Free Tier Notes

- Render free instances sleep after inactivity
- First request may take 30–60 seconds due to cold start
## Project Structure

```
.
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── llm.py             # Gemini-2.5-Flash model and prompts
│   ├── memory.py          # Session memory management
│   ├── graph.py           # LangGraph DAG definition
│   ├── calculator.py      # Calculator node
│   ├── monitoring.py      # Latency and throughput tracking
│   └── logging_utils.py   # Logger setup
├── logs/                  # Auto-created, stores *.log files
├── scripts/
│   ├── test_api.py                # Test script for /chat endpoint
│   ├── test_core_features.py      # Test core features (router, calculator, memory)
│   └── test_modules.py            # Test module imports
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
└── README.md              # This file
```

## Setup

### Prerequisites

- Python 3.11+
- Google Gemini API key (get one at https://makersuite.google.com/app/apikey)

### Local Installation

1. Clone the repository and navigate to the project:
```bash
cd MLops_task
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Google API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

Or set it as an environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"  # On Windows: set GEMINI_API_KEY=your_api_key_here
```

### Running Locally

Start the FastAPI server from the project root:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or from the app directory:
```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server runs at `http://localhost:8000`. Check health at `http://localhost:8000/health`. 

Access the test UI at `http://localhost:8000/test_ui`.

### Testing

Run the test suite in another terminal:

**Test 1: Core Features (Router, Calculator, Memory, Monitoring)**
```bash
cd scripts
python test_core_features.py
```

**Test 2: Module Imports**
```bash
python test_modules.py
```

Check `logs/` directory for request logs after running tests.

## Docker

### Build the Image

```bash
docker build -t llm-chatbot:latest .
```

### Run the Container

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_api_key_here" \
  -v $(pwd)/logs:/app/logs \
  llm-chatbot:latest
```

On Windows (PowerShell):
```powershell
docker run -p 8000:8000 `
  -e GEMINI_API_KEY="your_api_key_here" `
  -v ${PWD}/logs:/app/logs `
  llm-chatbot:latest
```

The service will be available at `http://localhost:8000`.

## API

### POST /chat

Send a message and get a response.

**Request:**
```json
{
  "session_id": "user123",
  "message": "Hello"
}
```

**Response:**
```json
{
  "response": "Hi! How can I help you?",
  "session_id": "user123"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Multi-User Sessions

Each `session_id` maintains separate conversation memory:

```python
# User 1
POST /chat with session_id="alice", message="My name is Alice"
POST /chat with session_id="alice", message="What's my name?"  # Remembers Alice

# User 2 (separate memory)
POST /chat with session_id="bob", message="I'm Bob"
POST /chat with session_id="bob", message="Who am I?"  # Remembers Bob, not Alice
```

**Note:** Memory is stored in-memory and will be lost when the server restarts. For production, replace the dictionary in `memory.py` with a persistent store (Redis, PostgreSQL, etc.).

## LangGraph DAG

The routing DAG is defined in `graph.py`:

```
Input → Router → [Calculator OR LLM] → Output
```

**Router Logic:**
- If input contains numbers + math operators → Calculator node
- Else → LLM node

The router is simple and heuristic-based. To add complexity, modify `router_node()` in `graph.py`.

## Prompts

Three prompt variants are defined in `llm.py`:

- **professional**: Concise, business-like responses
- **friendly**: Conversational, approachable tone
- **minimal**: Very brief answers

The **professional** variant is used by default. Switch by changing `DEFAULT_PROMPT_KEY` in `llm.py` or Change the Variant in the live_test_ui where you can see the dropdown to select the Variant 

## Monitoring

Each request logs:
- Session ID and input message
- Latency (seconds)
- Routing decision
- Response snippet

View logs:
```bash
tail -f logs/main.log          # API requests
tail -f logs/llm.log           # LLM operations
tail -f logs/graph.log         # Graph routing
tail -f logs/monitoring.log    # Latency and throughput
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Limitations

- **Session Storage**: In-memory only. Sessions are lost on restart.
- **Concurrency**: No database locks. If multiple threads modify the same session, behavior is undefined.
- **Calculator**: Simple math expressions only (no functions or variables).

## Troubleshooting

**ImportError: No module named 'langchain'**
```bash
pip install -r requirements.txt
```

**GEMINI_API_KEY not set**

Create a `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

Or set environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"  # On Windows: set GEMINI_API_KEY=your_api_key_here
```

**Port 8000 already in use**
```bash
python -c "import app.main; import uvicorn; uvicorn.run(app.main.app, host='0.0.0.0', port=8001)"
```
