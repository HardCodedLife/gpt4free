# PROJECT BRIEF: G4F Chatbot with Ollama Integration

## Project Overview

Building a free, public-access chatbot by forking [gpt4free](https://github.com/xtekky/gpt4free) and integrating a custom Ollama server to provide AI chat capabilities alongside existing free providers.

---

## Core Objectives

1. **Fork & Customize gpt4free**: Create custom Ollama provider integration
2. **Use Existing GUI**: Leverage g4f's web interface (no custom frontend needed)
3. **Public Access**: Deploy for community use with proper security
4. **Full Feature Set**: Support text chat, model switching, web search, file upload, voice, and image generation

---

## Technical Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: Flask (g4f built-in)
- **Base Project**: gpt4free (g4f)
- **AI Backend**: Ollama server at `http://100.92.194.37:11434`

### Frontend
- **Interface**: g4f existing GUI (web-based)
- **Modifications**: Model listing and switching UI

### Deployment
- **Environment**: Separate server from Ollama
- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: systemd
- **SSL**: Let's Encrypt (Certbot)

---

## Feature Requirements

### Must-Have (MVP)
- [x] Basic text chat with Ollama models
- [x] Dynamic model listing from Ollama API
- [x] Model switching in GUI
- [x] Streaming responses
- [x] Error handling & fallbacks

### Phase 2 Features
- [ ] Web search integration (g4f built-in)
- [ ] File upload and analysis
- [ ] Voice input/output
- [ ] Image generation (via g4f providers)

### Phase 3 (Post-Launch)
- [ ] Rate limiting per user
- [ ] Usage analytics
- [ ] User authentication (optional)
- [ ] API key system

---

## Architecture

### Provider Integration
```
g4f/Provider/Ollama.py
├── OllamaProvider class (AsyncGeneratorProvider)
├── get_models() - Fetch from Ollama /api/tags
├── create_async_generator() - Handle chat streaming
└── Error handling & retry logic
```

### API Endpoints
```
/api/ollama/models - GET list of available Ollama models
/api/chat - POST chat completion (existing g4f endpoint)
/api/upload - POST file upload (for analysis)
```

### GUI Modifications
```
g4f/gui/
├── Add Ollama model fetching on load
├── Populate model dropdown with Ollama models
└── Handle model switching events
```

---

## Ollama Server Details

**Base URL**: `http://100.92.194.37:11434`

**API Endpoints Used**:
- `GET /api/tags` - List available models
- `POST /api/chat` - Chat completion with streaming

**Expected Models**: Dynamic (fetched at runtime)
- Will support any models installed on Ollama server
- User can switch between models via GUI dropdown

---

## Security Considerations

### Required Security Measures
1. **Rate Limiting**: 30 requests/minute per IP
2. **Input Validation**: Sanitize all user inputs
3. **File Upload Limits**: Max 10MB file size
4. **CORS Configuration**: Restrict to specific domains (production)
5. **SSL/TLS**: HTTPS only in production
6. **Error Messages**: No sensitive info exposure

### Access Control
- Public read access to chat
- Rate limiting to prevent abuse
- Optional: Authentication for advanced features (future)

---

## Deployment Plan

### Development Environment
- Local machine with Python 3.10+
- Access to Ollama server for testing
- Git version control

### Production Environment
- **Server**: Ubuntu 20.04+ VPS
- **Domain**: TBD (user to provide)
- **Resources**: Minimum 2GB RAM, 2 CPU cores
- **Network**: Must reach Ollama server at `100.92.194.37:11434`

### Deployment Steps
1. Clone forked repo to production server
2. Install dependencies in virtual environment
3. Configure environment variables
4. Set up systemd service
5. Configure Nginx reverse proxy
6. Obtain SSL certificate
7. Enable firewall rules
8. Start and monitor service

---

## Success Criteria

### Technical Success
- ✅ Ollama models appear in GUI model list
- ✅ Chat responses stream correctly
- ✅ Can switch between models without errors
- ✅ Error handling when Ollama unavailable
- ✅ Response time < 2 seconds for first token
- ✅ 99% uptime over 30 days

### User Experience Success
- ✅ Intuitive model selection interface
- ✅ Fast response times
- ✅ Clear error messages
- ✅ Mobile-responsive design (inherited from g4f)

---

## Known Constraints

### Technical Limitations
- Ollama server is external (network dependency)
- No control over Ollama uptime
- Limited by Ollama server performance
- Python async required for streaming

### User Experience
- Must use g4f GUI (limited customization)
- Model availability depends on Ollama server

### Developer Constraints
- Limited Docker experience (avoid complex containerization)
- Need clear, step-by-step guidance
- Prefer Python/JS over other languages

---

## Risk Management

### Risk: Ollama Server Downtime
- **Mitigation**: Implement retry logic with exponential backoff
- **Fallback**: Show clear error message, suggest trying other g4f providers
- **Monitoring**: Health check endpoint, alerting

### Risk: Public Abuse
- **Mitigation**: Rate limiting, CAPTCHA (if needed)
- **Monitoring**: Track request patterns, IP-based blocking

### Risk: Breaking Changes in g4f
- **Mitigation**: Fork at stable release, test before updates
- **Strategy**: Document all custom modifications

---

## Development Phases

### Phase 1: Core Integration (Week 1-2)
- Set up development environment
- Create Ollama provider
- Test basic chat functionality
- Integrate with g4f provider system

### Phase 2: GUI Enhancement (Week 3)
- Add model listing API endpoint
- Modify GUI for Ollama model display
- Implement model switching

### Phase 3: Additional Features (Week 4-5)
- Web search integration
- File upload support
- Voice/audio features
- Image generation

### Phase 4: Security & Polish (Week 6)
- Implement rate limiting
- Add comprehensive error handling
- Security hardening
- Performance optimization

### Phase 5: Testing (Week 7)
- Unit tests for provider
- Integration tests
- Load testing
- Security testing

### Phase 6: Deployment (Week 8)
- Production server setup
- Nginx configuration
- SSL setup
- Monitoring implementation

### Phase 7: Documentation (Week 8-9)
- User documentation
- API documentation
- Deployment guide
- Troubleshooting guide

---

## File Structure

```
gpt4free/ (forked repo)
├── g4f/
│   ├── Provider/
│   │   ├── __init__.py (modified)
│   │   ├── Ollama.py (new)
│   │   └── BaseProvider.py (reference)
│   ├── gui/
│   │   ├── client/ (may need modifications)
│   │   └── server/
│   │       └── backend_api.py (add endpoints)
│   ├── models.py (add Ollama models)
│   └── client.py (existing)
├── tests/
│   └── test_ollama.py (new)
├── docs/
│   ├── PROJECT-BRIEF.md (this file)
│   ├── TODO.md
│   ├── INTEGRATION-GUIDE.md
│   └── API-DOCS.md
├── .env.example (new)
├── requirements.txt (existing)
└── README.md (update)
```

---

## Key Dependencies

### Python Packages
- `g4f` - Base framework
- `aiohttp` - Async HTTP client
- `flask` - Web framework
- `flask-cors` - CORS handling
- `flask-limiter` - Rate limiting
- `gunicorn` - Production WSGI server
- `pytest` - Testing
- `pytest-asyncio` - Async testing

### System Dependencies
- Python 3.10+
- Nginx
- Certbot
- Git

---

## Testing Strategy

### Unit Tests
- Provider connection tests
- Model fetching tests
- Chat completion tests
- Error handling tests

### Integration Tests
- End-to-end chat flow
- Model switching
- File upload
- Web search integration

### Load Tests
- Concurrent user simulation
- Rate limiting verification
- Performance benchmarks

### Security Tests
- Input validation
- XSS prevention
- Rate limit bypass attempts
- Authentication (if implemented)

---

## Monitoring & Maintenance

### Metrics to Track
- Request count per endpoint
- Response times
- Error rates
- Ollama server availability
- Active users
- Model usage distribution

### Tools
- Application logs (rotating file handler)
- System monitoring (htop, netdata)
- Error tracking (application-level)
- Uptime monitoring (external service)

### Maintenance Tasks
- Daily: Check logs for errors
- Weekly: Review usage metrics
- Monthly: Update dependencies
- Quarterly: Security audit

---

## Resources

### Documentation
- [g4f GitHub](https://github.com/xtekky/gpt4free)
- [g4f Documentation](https://g4f.dev/docs)
- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Community
- g4f Discord: [discord.gg/qXA4Wf4Fsm](https://discord.gg/qXA4Wf4Fsm)
- g4f Telegram: [telegram.me/g4f_channel](https://telegram.me/g4f_channel)

### Reference Implementations
- g4f/Provider/Bing.py - Streaming example
- g4f/Provider/BaseProvider.py - Provider interface
- g4f/gui/ - Existing GUI structure

---

## Contact & Collaboration

**Project Owner**: [Your Name/Handle]
**Repository**: [Your Fork URL]
**Ollama Server**: Maintained separately
**Support**: [Discord/Email/Issue Tracker]

---

## Version History

- **v0.1** (Current) - Project brief created
- **v1.0** (Target) - MVP with Ollama integration
- **v1.1** (Target) - All features implemented
- **v2.0** (Future) - Additional models and authentication

---

## Notes for Claude Code

When working on this project:

1. **Always check existing g4f patterns** before implementing
2. **Test Ollama connectivity** before blaming code
3. **Use async/await** for all I/O operations
4. **Follow PEP 8** style guidelines
5. **Add docstrings** to all functions
6. **Handle errors gracefully** (Ollama may be down)
7. **Keep commits atomic** - one feature per commit
8. **Reference this brief** when making architectural decisions

---

**Last Updated**: [2025-10-10] \
**Status**: Planning Phase \
**Next Milestone**: Phase 1 - Core Integration