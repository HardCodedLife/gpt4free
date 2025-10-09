# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fork of **gpt4free** (g4f) - a Python library providing unified access to 108+ AI providers. The fork adds **Ollama integration** to enable a custom chatbot with models hosted on a private Ollama server (`http://100.92.194.37:11434`).

**Core Goal**: Create a public-access chatbot that combines g4f's existing providers with custom Ollama models, using g4f's existing web GUI.

## Essential Commands

### Installation & Setup
```bash
# Install dependencies (2-5 min - DO NOT CANCEL, use 600s+ timeout)
pip install -r requirements.txt

# Remove CI-only dependency
pip uninstall -y nodriver

# Install in editable mode (30-60s, use 120s+ timeout)
pip install -e .

# Alternative: minimal install
pip install -r requirements-min.txt
```

### Testing
```bash
# Run unit tests (expect ~41 tests, 1-2 failures OK in isolated env)
python -m etc.unittest

# Quick import test
python -c "from g4f.client import Client; print('OK')"
```

### Running the Application
```bash
# Start API server with GUI (http://localhost:8080)
python -m g4f --port 8080

# API server only
python -m g4f.cli api --port 8080

# GUI server
python -m g4f.cli gui --port 8080 --debug

# CLI help
g4f --help
```

## Architecture: The Big Picture

### Provider System
g4f uses a **provider abstraction** where each AI service is implemented as a provider class:

- **Location**: `g4f/Provider/` (user-facing) wraps `g4f/providers/` (core implementation)
- **Base Classes**:
  - `AsyncGeneratorProvider` - For streaming responses with async generators
  - `OpenaiTemplate` - For OpenAI-compatible APIs (inherits from AsyncGeneratorProvider)
  - `AbstractProvider` - Synchronous provider base
- **Registration**: Providers must be imported in `g4f/Provider/__init__.py` to be available system-wide

### Provider Implementation Pattern

Every provider follows this structure:
```python
class MyProvider(AsyncGeneratorProvider, ProviderModelMixin):
    url = "https://provider.com"
    working = True
    supports_stream = True
    supports_message_history = True
    default_model = "model-name"

    @classmethod
    def get_models(cls) -> list[str]:
        # Fetch or return available models

    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        stream: bool = True,
        **kwargs
    ) -> AsyncResult:
        # Yield response chunks for streaming
```

**Key Insight**: All I/O operations use async/await. Providers yield chunks for streaming or full responses for non-streaming modes.

### GUI & API Server

The web interface is a Flask application with two key components:

1. **Backend API** (`g4f/gui/server/backend_api.py`):
   - Handles `/api/*` endpoints
   - Routes chat completions to providers
   - Manages file uploads, model selection, conversations
   - Flask routes are registered in `Backend_Api.__init__()`

2. **Frontend** (`g4f/gui/`):
   - Web interface served by Flask
   - Communicates with backend via `/api/*` endpoints
   - Model selection, chat UI, settings

**To add API endpoints**: Modify `backend_api.py` and add routes to the `Backend_Api` class.

### Request Flow

```
User (Browser)
  ↓
Flask GUI Server (g4f/gui/server/app.py)
  ↓
Backend API (g4f/gui/server/backend_api.py)
  ↓
Client Service (g4f/client/service.py) - converts provider/model selection
  ↓
Provider (g4f/Provider/ProviderName.py) - create_async_generator()
  ↓
External API (OpenAI, Anthropic, Ollama, etc.)
```

## Ollama Integration Architecture

### Custom Ollama Server Details
- **Base URL**: `http://100.92.194.37:11434`
- **Key Endpoints**:
  - `GET /api/tags` - List available models
  - `POST /api/chat` - Chat completion (streaming supported)
- **Models**: Dynamically fetched at runtime

### Ollama Provider Implementation

The Ollama provider (`g4f/Provider/Ollama.py`) should:
1. Extend `AsyncGeneratorProvider` and `ProviderModelMixin`
2. Implement `get_models()` to fetch from `/api/tags`
3. Implement `create_async_generator()` to:
   - Format messages for Ollama API
   - POST to `/api/chat` with streaming
   - Parse NDJSON response lines
   - Yield content chunks
4. Handle errors when Ollama server is unreachable
5. Use retry logic with timeouts

### GUI Integration for Ollama

To display Ollama models in the GUI:
1. Add `/api/ollama/models` endpoint in `backend_api.py`
2. Frontend calls this on page load
3. Populate model dropdown with "Ollama: {model_name}" entries
4. When user selects Ollama model, backend routes to Ollama provider

## Critical Development Guidelines

### Async/Await Everywhere
This codebase uses async heavily. All I/O (HTTP requests, file operations) must use:
- `aiohttp.ClientSession` for HTTP
- `async with` for context managers
- `await` for coroutines
- `async for` for streaming responses

### Provider Registration Checklist
When adding a provider:
1. Create `g4f/Provider/YourProvider.py`
2. Import in `g4f/Provider/__init__.py`
3. Add to `__all__` list
4. Test with: `python -c "from g4f.Provider import YourProvider; print(YourProvider)"`

### Testing Requirements
- Always run `python -m etc.unittest` after changes
- Test streaming: Verify chunks are yielded incrementally
- Test error handling: Disconnect provider, ensure graceful failure
- Test model switching: Ensure Ollama and g4f providers coexist

### Security for Public Deployment
This chatbot will be public-facing. Critical security measures:
- **Rate limiting**: Use `flask-limiter` (30 req/min per IP)
- **Input validation**: Sanitize all user inputs
- **File uploads**: Validate types and sizes (max 10MB)
- **CORS**: Configure properly for production domain
- **No hardcoded secrets**: Use environment variables

## Common Development Tasks

### Creating a New Provider
1. Study existing provider: `g4f/Provider/DeepInfra.py` (OpenAI-compatible) or `g4f/Provider/Perplexity.py` (custom)
2. Copy structure, modify API calls
3. Implement `get_models()` and `create_async_generator()`
4. Register in `__init__.py`
5. Test with simple completion

### Adding API Endpoints
1. Open `g4f/gui/server/backend_api.py`
2. Add method to `Backend_Api` class:
   ```python
   @app.route('/api/my-endpoint', methods=['POST'])
   def my_endpoint():
       # Implementation
       return jsonify({"result": "data"})
   ```
3. Frontend can now fetch from `/api/my-endpoint`

### Running a Single Test
```bash
# Test specific provider
python -c "from g4f.Provider import Ollama; import asyncio; asyncio.run(Ollama.get_models())"

# Test API server startup
python -m g4f --port 8080 &
curl http://localhost:8080/api/models
```

## Important Files

### Core Provider Infrastructure
- `g4f/providers/base_provider.py` - Base provider classes (AbstractProvider, AsyncGeneratorProvider)
- `g4f/Provider/template/OpenaiTemplate.py` - Template for OpenAI-compatible providers
- `g4f/Provider/__init__.py` - Provider registry (MUST import new providers here)

### API & GUI
- `g4f/gui/server/backend_api.py` - Flask routes for API endpoints
- `g4f/gui/server/app.py` - Main Flask app setup
- `g4f/api/run.py` - FastAPI server entry point

### Configuration
- `setup.py` - Package metadata, dependencies, entry points
- `g4f/config.py` - Global configuration
- `requirements.txt` - Full dependencies
- `requirements-min.txt` - Minimal dependencies

## Project-Specific Patterns

### Error Handling Pattern
```python
from ...errors import MissingAuthError, ModelNotFoundError

try:
    response = await session.post(url, json=data)
    response.raise_for_status()
except asyncio.TimeoutError:
    raise TimeoutError("Provider timeout")
except Exception as e:
    raise ResponseError(f"Provider error: {e}")
```

### Streaming Response Pattern
```python
async for line in response.content:
    if line:
        try:
            data = json.loads(line)
            if "content" in data:
                yield data["content"]
        except json.JSONDecodeError:
            continue
```

### Model Selection Pattern
```python
# Providers expose models via get_models()
@classmethod
def get_models(cls) -> list[str]:
    if not cls.models:
        # Fetch from API or return static list
        cls.models = fetch_models_from_api()
    return cls.models
```

## Environment Variables

For Ollama integration, use these environment variables:
```bash
OLLAMA_BASE_URL=http://100.92.194.37:11434
OLLAMA_TIMEOUT=120
G4F_PORT=8080
G4F_DEBUG=False
RATE_LIMIT_PER_MINUTE=30
```

Load with `python-dotenv`:
```python
from dotenv import load_dotenv
import os
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://100.92.194.37:11434")
```

## Dependencies

### Core
- Python 3.10+ (3.12 recommended)
- aiohttp - Async HTTP client
- requests - Sync HTTP (for simple operations)
- flask - GUI server
- fastapi - API server

### Optional but Commonly Used
- curl_cffi - Browser impersonation
- beautifulsoup4 - HTML parsing
- pillow - Image processing
- pytest - Testing

Install groups:
- `[all]` - Everything
- `[gui]` - GUI only
- `[api]` - API server only
- `[slim]` - Minimal runtime

## Known Issues & Workarounds

1. **Long install times**: `pip install -r requirements.txt` takes 2-5 minutes. Set timeout to 600+ seconds.
2. **Unit test failures**: 1-2 network-related failures expected in isolated environments.
3. **pydub ffmpeg warning**: Harmless, ignore it.
4. **Provider availability**: Many providers may fail due to network restrictions or API changes.
5. **Ollama dependency**: This fork depends on external Ollama server availability.

## When Making Changes

### Before Starting
1. Understand the provider pattern by reading 2-3 existing providers
2. Review `base_provider.py` to understand inheritance hierarchy
3. Test Ollama server connectivity: `curl http://100.92.194.37:11434/api/tags`

### During Development
1. Use type hints everywhere: `def func(param: str) -> AsyncResult:`
2. Follow PEP 8 style
3. Add docstrings to classes and methods
4. Test incrementally - don't stack untested changes
5. Use `g4f/debug.py` for logging: `debug.log("message")`

### After Changes
1. Run unit tests: `python -m etc.unittest`
2. Test manual workflow: Start server, send chat request
3. Check for import errors: `python -c "import g4f"`
4. Verify provider registration: `g4f --help` should list providers

## Additional Resources

- **Main docs**: https://g4f.dev/docs
- **Provider creation guide**: https://g4f.dev/docs/guides/create_provider
- **Ollama API docs**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Project brief**: See `PROJECT-BRIEF.md` in repo
- **TODO list**: See `TODO.md` for implementation checklist
- **Development plan**: See `PLAN.md` for detailed phase breakdown
