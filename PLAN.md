# Comprehensive Plan: Building Your Free Chatbot with Ollama Integration

## Project Overview
You'll fork gpt4free, create a custom Ollama provider, and deploy it with the existing GUI to allow public access to your Ollama models alongside other free providers.

---

## Phase 1: Environment Setup & Understanding (Week 1)

### 1.1 Fork and Clone the Repository
```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/gpt4free.git
cd gpt4free
git checkout -b ollama-integration
```

### 1.2 Set Up Development Environment
```bash
# Install Python 3.10+
python --version  # Verify version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for all features
pip install -U g4f[all]
```

### 1.3 Test Ollama Server Connectivity
Create a test script `test_ollama.py`:
```python
import requests
import json

OLLAMA_BASE_URL = "http://100.92.194.37:11434"

# Test 1: Check server is alive
response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
print("Available models:", json.dumps(response.json(), indent=2))

# Test 2: Test chat completion
test_data = {
    "model": "llama3",  # Change to your model name
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": False
}
response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=test_data)
print("Chat response:", response.json())
```

### 1.4 Understand g4f Project Structure
Key directories to familiarize yourself with:
- `g4f/Provider/` - Where all provider implementations live
- `g4f/gui/` - Web interface files
- `g4f/client.py` - Client API
- `g4f/models.py` - Model definitions

---

## Phase 2: Create Custom Ollama Provider (Week 2)

### 2.1 Create Provider File
Create `g4f/Provider/Ollama.py`:

```python
from __future__ import annotations

import json
import requests
from aiohttp import ClientSession
from typing import AsyncGenerator, Optional

from ..typing import AsyncResult, Messages
from .base_provider import AsyncGeneratorProvider, ProviderModelMixin
from .helper import format_prompt


class Ollama(AsyncGeneratorProvider, ProviderModelMixin):
    """Custom provider for Ollama server integration"""
    
    url = "http://100.92.194.37:11434"
    working = True
    supports_stream = True
    supports_system_message = True
    supports_message_history = True
    
    # Default models - will be dynamically fetched
    default_model = "llama3"
    models = []
    
    @classmethod
    def get_models(cls) -> list[str]:
        """Fetch available models from Ollama server"""
        try:
            response = requests.get(f"{cls.url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                cls.models = [model['name'] for model in data.get('models', [])]
                return cls.models
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
        return [cls.default_model]
    
    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        stream: bool = True,
        proxy: str = None,
        **kwargs
    ) -> AsyncResult:
        """Generate responses from Ollama"""
        
        if not cls.models:
            cls.get_models()
        
        # Use default model if specified model not available
        if model not in cls.models and cls.models:
            model = cls.default_model
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Format messages for Ollama API
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        data = {
            "model": model,
            "messages": formatted_messages,
            "stream": stream,
            "options": kwargs.get("options", {})
        }
        
        async with ClientSession() as session:
            async with session.post(
                f"{cls.url}/api/chat",
                headers=headers,
                json=data,
                proxy=proxy
            ) as response:
                response.raise_for_status()
                
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                json_response = json.loads(line)
                                if "message" in json_response:
                                    content = json_response["message"].get("content", "")
                                    if content:
                                        yield content
                                
                                # Check if done
                                if json_response.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    result = await response.json()
                    if "message" in result:
                        yield result["message"].get("content", "")
```

### 2.2 Register Provider
Edit `g4f/Provider/__init__.py` and add:
```python
from .Ollama import Ollama

__all__ = [
    # ... existing providers ...
    'Ollama',
]
```

### 2.3 Add Models to Model List
Edit `g4f/models.py` and add:
```python
# Ollama Models (dynamically loaded)
class OllamaModel:
    """Dynamic Ollama model class"""
    pass

# You can also define specific models if you know them:
ollama_llama3 = Model(
    name='ollama/llama3',
    base_provider='Ollama',
    best_provider=Ollama
)
```

---

## Phase 3: Modify GUI for Model Listing (Week 3)

### 3.1 Update Backend API
Edit `g4f/api/__init__.py` or create new endpoint in `g4f/gui/server/backend_api.py`:

```python
from flask import jsonify
from g4f.Provider.Ollama import Ollama

@app.route('/api/ollama/models')
def get_ollama_models():
    """Endpoint to fetch Ollama models"""
    try:
        models = Ollama.get_models()
        return jsonify({
            'success': True,
            'models': models,
            'provider': 'Ollama'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 3.2 Update Frontend Model Selection
Locate the GUI files (usually in `g4f/gui/client/` or similar) and modify the model selector component:

```javascript
// In the model selection component
async function fetchOllamaModels() {
    try {
        const response = await fetch('/api/ollama/models');
        const data = await response.json();
        
        if (data.success) {
            // Add Ollama models to the model list
            const ollamaModels = data.models.map(model => ({
                name: `Ollama: ${model}`,
                value: model,
                provider: 'Ollama'
            }));
            
            // Merge with existing models
            updateModelList(ollamaModels);
        }
    } catch (error) {
        console.error('Failed to fetch Ollama models:', error);
    }
}

// Call on component mount
fetchOllamaModels();
```

---

## Phase 4: Configure Additional Features (Week 4)

### 4.1 Enable Web Search Integration
g4f already has web search. Ensure it's enabled in your configuration:

```python
# In your chat handler
from g4f.client import Client

client = Client()
response = client.chat.completions.create(
    model="ollama/llama3",
    messages=[{"role": "user", "content": "Search the web for latest AI news"}],
    web_search=True  # Enable web search
)
```

### 4.2 File Upload/Analysis
g4f supports file handling. You need to ensure the GUI has file upload enabled:

```python
# Backend endpoint for file upload
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    # Process file and store temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    return jsonify({
        'success': True,
        'file_path': file_path,
        'filename': file.filename
    })
```

### 4.3 Image Generation
Add image generation provider alongside Ollama:

```python
# Use existing image providers in g4f
from g4f.client import Client

client = Client()

# For image generation
image_response = client.images.generate(
    model="flux",  # or other available image models
    prompt="a beautiful landscape",
    response_format="url"
)
```

### 4.4 Voice/Audio Features
Enable speech recognition and TTS in the GUI:

```javascript
// Frontend: Add speech recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
};

// Start listening
function startVoiceInput() {
    recognition.start();
}

// Text-to-speech
function speakResponse(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
}
```

---

## Phase 5: Security & Configuration (Week 5)

### 5.1 Environment Configuration
Create `.env` file:
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://100.92.194.37:11434
OLLAMA_TIMEOUT=120

# Server Configuration
G4F_HOST=0.0.0.0
G4F_PORT=8080
G4F_DEBUG=False

# Security
ALLOWED_ORIGINS=*
RATE_LIMIT_ENABLED=True
MAX_REQUESTS_PER_MINUTE=60

# Features
WEB_SEARCH_ENABLED=True
FILE_UPLOAD_ENABLED=True
MAX_FILE_SIZE_MB=10
```

### 5.2 Add Rate Limiting
Install flask-limiter:
```bash
pip install flask-limiter
```

Add to your Flask app:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

@app.route('/api/chat')
@limiter.limit("30 per minute")
def chat():
    # Your chat endpoint
    pass
```

### 5.3 CORS Configuration
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # In production, specify your domain
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 5.4 Security Headers
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Phase 6: Testing (Week 6)

### 6.1 Unit Tests
Create `tests/test_ollama_provider.py`:
```python
import pytest
from g4f.Provider.Ollama import Ollama

def test_ollama_connection():
    """Test Ollama server connection"""
    models = Ollama.get_models()
    assert len(models) > 0

@pytest.mark.asyncio
async def test_ollama_chat():
    """Test chat completion"""
    messages = [{"role": "user", "content": "Hello"}]
    
    response_text = ""
    async for chunk in Ollama.create_async_generator(
        model="llama3",
        messages=messages,
        stream=True
    ):
        response_text += chunk
    
    assert len(response_text) > 0
```

Run tests:
```bash
pytest tests/
```

### 6.2 Local Testing
```bash
# Start the GUI locally
python -m g4f.cli gui --port 8080 --debug

# Or using the Python API
python -m g4f --port 8080 --debug
```

Access at: `http://localhost:8080/chat/`

### 6.3 Test All Features
Create a test checklist:
- [ ] Model listing shows Ollama models
- [ ] Can switch between different Ollama models
- [ ] Chat responses work correctly
- [ ] Streaming responses work
- [ ] Web search integration works
- [ ] File upload works
- [ ] Image generation works
- [ ] Voice input/output works
- [ ] Rate limiting works
- [ ] Error handling works properly

---

## Phase 7: Deployment (Week 7)

### 7.1 Prepare Production Server

**Server Requirements:**
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.10+
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt)
- Minimum 2GB RAM, 2 CPU cores

### 7.2 Install Dependencies on Production Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 7.3 Deploy Application
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/gpt4free.git
cd gpt4free

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### 7.4 Create Systemd Service
Create `/etc/systemd/system/g4f-chatbot.service`:
```ini
[Unit]
Description=G4F Chatbot Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/gpt4free
Environment="PATH=/path/to/gpt4free/venv/bin"
ExecStart=/path/to/gpt4free/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8080 g4f.api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable g4f-chatbot
sudo systemctl start g4f-chatbot
sudo systemctl status g4f-chatbot
```

### 7.5 Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/g4f-chatbot`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=chatbot_limit:10m rate=30r/m;
    limit_req zone=chatbot_limit burst=10 nodelay;

    # Max upload size
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket support for streaming
    location /ws {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/g4f-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7.6 Setup SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 7.7 Firewall Configuration
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Phase 8: Monitoring & Maintenance (Ongoing)

### 8.1 Setup Logging
Create logging configuration in your app:
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

### 8.2 Monitor Server Resources
Install monitoring tools:
```bash
# Install htop for process monitoring
sudo apt install htop -y

# Install netdata for comprehensive monitoring
bash <(curl -Ss https://get.netdata.cloud/kickstart.sh)
```

### 8.3 Setup Automated Backups
Create backup script `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/g4f-chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup application code
tar -czf "$BACKUP_DIR/code_$DATE.tar.gz" /path/to/gpt4free

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" /path/to/gpt4free/logs

# Keep only last 7 backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### 8.4 Update Strategy
Create update script `update.sh`:
```bash
#!/bin/bash
cd /path/to/gpt4free
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart g4f-chatbot
```

---

## Phase 9: Documentation (Week 8)

### 9.1 Create README for Your Fork
```markdown
# G4F Chatbot with Ollama Integration

Custom chatbot built on gpt4free with integrated Ollama server support.

## Features
- Multiple AI model support (GPT, Claude, Ollama, etc.)
- Web search integration
- File upload and analysis
- Voice input/output
- Image generation
- Real-time streaming responses

## Setup
[Installation instructions]

## API Documentation
[API endpoints and usage]

## Contributing
[How to contribute]
```

### 9.2 Create User Guide
Document for end-users:
- How to select models
- How to use different features
- Tips for best results
- FAQ

### 9.3 Create API Documentation
If exposing API endpoints:
```python
# Use Flask-RESTX or similar for auto-documentation
from flask_restx import Api, Resource

api = Api(app, version='1.0', title='G4F Ollama API',
    description='API for chatbot with Ollama integration')
```

---

## Estimated Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| 1. Setup | Week 1 | Environment ready, Ollama tested |
| 2. Provider Creation | Week 2 | Working Ollama provider |
| 3. GUI Modification | Week 3 | Model listing & switching |
| 4. Features | Week 4 | All features integrated |
| 5. Security | Week 5 | Secured application |
| 6. Testing | Week 6 | Fully tested system |
| 7. Deployment | Week 7 | Live production system |
| 8. Monitoring | Ongoing | Stable operations |
| 9. Documentation | Week 8 | Complete docs |

---

## Critical Success Factors

1. **Network Connectivity**: Ensure your deployment server can reach `http://100.92.194.37:11434`
2. **Ollama Server Stability**: Monitor Ollama server uptime and performance
3. **Rate Limiting**: Essential for public access to prevent abuse
4. **Error Handling**: Robust error handling for when Ollama is unavailable
5. **Fallback Strategy**: Consider adding fallback to other g4f providers when Ollama fails

---

## Troubleshooting Guide

### Common Issues:

**1. Can't connect to Ollama server**
```python
# Add connection retry logic
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_retry_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session
```

**2. Models not loading**
- Check Ollama server status
- Verify network connectivity
- Check firewall rules

**3. Streaming not working**
- Verify WebSocket configuration in Nginx
- Check browser console for errors
- Ensure proper CORS headers

---

## Next Steps After Completion

1. **Add Authentication**: Implement user accounts if needed
2. **Analytics**: Track usage patterns
3. **Custom Models**: Add more Ollama models
4. **Mobile App**: Create mobile interface
5. **API Keys**: Implement API key system for programmatic access

Would you like me to elaborate on any specific phase or create code examples for particular components?