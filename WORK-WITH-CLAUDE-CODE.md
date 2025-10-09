# Working Efficiently with Claude Code: Tips & Insights

## 1. **Project Context is King**

### Provide Clear Context Upfront
```bash
# Before starting, give Claude Code the big picture
claude-code "I'm integrating Ollama into gpt4free. The project structure:
- g4f/Provider/ contains provider implementations
- g4f/gui/ has the web interface
- Goal: Create Ollama.py provider and modify GUI for model listing
Current step: Creating the provider class"
```

**Why it matters**: Claude Code works much better when it understands:
- What you're building
- Where you are in the process
- What files are related
- Your specific constraints (Python version, existing architecture, etc.)

---

## 2. **Task Chunking Strategy**

### Break Complex Tasks Into Atomic Units
❌ **Too Broad**:
```bash
claude-code "Add Ollama integration to the entire project"
```

✅ **Atomic & Clear**:
```bash
# Step 1
claude-code "Create g4f/Provider/Ollama.py with AsyncGeneratorProvider base class that connects to http://100.92.194.37:11434/api/chat"

# Step 2
claude-code "Add Ollama to g4f/Provider/__init__.py exports"

# Step 3
claude-code "Create API endpoint in backend_api.py to fetch Ollama models from /api/tags"
```

**Best Size**: One task = One file or one logical unit of functionality

---

## 3. **Leverage File Context Intelligently**

### Explicitly Reference Files
```bash
# Point to specific files for context
claude-code "Look at g4f/Provider/Bing.py and create similar Ollama.py but using requests to Ollama API instead of browser automation"

# Or show it the pattern
claude-code "Following the pattern in g4f/Provider/BaseProvider.py, implement Ollama.py with these specific methods: get_models(), create_async_generator()"
```

**Pro Tip**: Claude Code can read multiple files at once. Use this for:
- Understanding existing patterns
- Ensuring consistency with codebase style
- Fixing related bugs across files

---

## 4. **Iterative Refinement > Perfect First Try**

### Embrace the Feedback Loop
```bash
# First pass - get something working
claude-code "Create basic Ollama provider with hardcoded model list"

# Test it, then refine
claude-code "The Ollama provider works but model list is hardcoded. Modify to fetch models dynamically from /api/tags endpoint with error handling"

# Polish
claude-code "Add retry logic and timeout handling to Ollama.get_models() method"
```

**Insight**: Don't aim for perfection initially. Get a working version, test it, then iterate. Claude Code is excellent at incremental improvements.

---

## 5. **Error Messages Are Your Friend**

### Always Include Full Error Context
```bash
# When something breaks
claude-code "Getting this error when running the provider:
```
AttributeError: module 'g4f.Provider' has no attribute 'Ollama'
```
Stack trace shows it's failing in __init__.py line 45.
The file g4f/Provider/Ollama.py exists and has the Ollama class.
Fix the import issue."
```

**What to include**:
- Full error message
- Stack trace
- What you were trying to do
- What file/line it's failing on
- Any relevant environment details

---

## 6. **Testing During Development**

### Ask for Test Code Alongside Implementation
```bash
claude-code "Create Ollama.py provider and also create tests/test_ollama.py with:
1. Test for server connectivity
2. Test for model fetching
3. Test for async chat completion
Use pytest-asyncio"
```

**Why**: Testing as you go catches issues early. Claude Code is great at generating test cases.

---

## 7. **Use Comments as Documentation**

### Have Claude Code Add Explanatory Comments
```bash
claude-code "Add detailed docstrings and inline comments to Ollama.py explaining:
- Why we use AsyncGeneratorProvider
- The Ollama API format
- Error handling strategy
- The streaming response format"
```

**Benefit**: Future you (and Claude Code in later sessions) will understand the code better.

---

## 8. **Specify Code Style & Patterns**

### Be Explicit About Conventions
```bash
claude-code "Create Ollama.py following these conventions:
- Use type hints for all functions
- Follow PEP 8 style
- Use async/await for all I/O operations
- Match the error handling pattern used in g4f/Provider/Bing.py
- Keep class attributes uppercase (like default_model)"
```

**Insight**: g4f has its own patterns. Point Claude Code to existing files as style references.

---

## 9. **Version Control Integration**

### Use Git Strategically
```bash
# Before major changes
git commit -m "Working basic provider"

# Then ask Claude Code for risky changes
claude-code "Refactor Ollama.py to use connection pooling"

# If it breaks, easy rollback
git diff  # Review changes
git checkout -- g4f/Provider/Ollama.py  # Revert if needed
```

**Pro Tip**: Commit working states frequently. Claude Code might introduce bugs—having checkpoints helps.

---

## 10. **Configuration & Environment Variables**

### Let Claude Code Handle Config Management
```bash
claude-code "Modify Ollama.py to read OLLAMA_BASE_URL from environment variables with fallback to 100.92.194.37:11434. Add .env.example file showing required variables."
```

**Good Practice**: Don't hardcode values. Claude Code can help you set up proper configuration management.

---

## 11. **Handle Multiple Files Changes**

### Coordinate Related Changes
```bash
claude-code "I need to add Ollama integration. This requires:
1. Creating g4f/Provider/Ollama.py
2. Updating g4f/Provider/__init__.py to export Ollama
3. Adding Ollama models to g4f/models.py
4. Creating /api/ollama/models endpoint in backend_api.py
Do these changes ensuring they work together."
```

**Insight**: Claude Code can handle multi-file changes. Just be clear about dependencies.

---

## 12. **Debugging Session Pattern**

### Structured Debugging Approach
```bash
# 1. Describe the problem
claude-code "Chat streaming isn't working. Messages appear all at once instead of word-by-word."

# 2. Show what you've tried
claude-code "I confirmed:
- Ollama API returns stream=true in request
- Response has done:false in chunks
- Frontend has EventSource set up
Still not streaming. Check Ollama.py generator logic."

# 3. Get targeted fix
claude-code "The issue is in create_async_generator. The yield is inside try/except but chunks aren't being flushed. Fix the streaming logic."
```

---

## 13. **Documentation Generation**

### Auto-Generate Docs
```bash
claude-code "Generate API documentation for all new endpoints in markdown format. Include:
- Endpoint URL
- Request format with example
- Response format with example
- Error codes
Save to docs/ollama-api.md"
```

---

## 14. **Security & Validation**

### Ask for Security Review
```bash
claude-code "Review Ollama.py for security issues:
- Input validation
- SQL injection risks (if any)
- XSS vulnerabilities
- Rate limiting needs
- Authentication requirements for public access
Add necessary security measures."
```

---

## 15. **Performance Optimization**

### Profile Then Optimize
```bash
# Don't optimize prematurely
claude-code "The model fetching is slow. Add caching to Ollama.get_models() with 5-minute TTL. Use functools.lru_cache or similar."
```

---

## 16. **Migration & Refactoring**

### Gradual Migration Strategy
```bash
# When changing existing code
claude-code "The old chat handler is in legacy.py. Create new handler in Ollama.py that:
1. Works alongside old handler
2. Has feature parity
3. Can be tested independently
Then we'll migrate gradually."
```

---

## 17. **Common Pitfalls to Avoid**

### ❌ What NOT to Do:

**1. Vague Requests**
```bash
# Bad
claude-code "Fix the bug"

# Good
claude-code "Fix the AttributeError in line 45 of Ollama.py where 'messages' is undefined"
```

**2. Assuming Context**
```bash
# Bad
claude-code "Add that feature we discussed"

# Good
claude-code "Add model switching dropdown to the GUI that calls /api/ollama/models endpoint"
```

**3. Too Many Changes at Once**
```bash
# Bad
claude-code "Add Ollama, fix all bugs, refactor GUI, add tests, deploy"

# Good
claude-code "Add Ollama provider first, then we'll tackle other tasks"
```

---

## 18. **Advanced: Working with External APIs**

### Test API Integration Separately
```bash
# First, test the API manually
claude-code "Create a standalone script test_ollama_api.py that:
1. Calls /api/tags to get models
2. Calls /api/chat with test message
3. Prints responses
This helps verify Ollama server before integrating into g4f."
```

---

## 19. **Code Review Checklist**

### Ask Claude Code to Self-Review
```bash
claude-code "Review the Ollama.py file and check:
- Are all edge cases handled?
- Is error handling comprehensive?
- Are there any potential memory leaks?
- Is the code maintainable?
- Does it follow g4f patterns?
Create a checklist of issues found."
```

---

## 20. **Collaboration & Handoff**

### Prepare for Team Work
```bash
claude-code "I'm handing off this Ollama integration to another developer. Create:
1. INTEGRATION_GUIDE.md with setup steps
2. Inline comments explaining non-obvious code
3. TODO.md with remaining tasks
4. Known issues documented"
```

---

## Golden Rules for Claude Code

1. **Be Specific**: Vague requests = vague results
2. **Provide Context**: Show related files, explain the goal
3. **Iterate Quickly**: Small changes > large rewrites
4. **Test Frequently**: Don't stack untested changes
5. **Use Examples**: "Like file X but for Y" works great
6. **Ask for Explanation**: "Explain why this approach" helps you learn
7. **Review Changes**: Always check the diff before committing
8. **Save Working States**: Git commit before major changes

---

## Specific to Your Project

### For gpt4free + Ollama Integration:

```bash
# Start with provider
claude-code "Create g4f/Provider/Ollama.py based on g4f/Provider/Bing.py structure but using HTTP requests to Ollama API at http://100.92.194.37:11434"

# Then test it
claude-code "Create simple test script to verify Ollama provider works with llama3 model"

# Then integrate to GUI
claude-code "Add model fetching endpoint and modify GUI to show Ollama models in dropdown"

# Then add features one by one
claude-code "Add file upload support to Ollama provider for document analysis"
```

**Key Insight**: For this project, you'll be spending most time on:
1. **Provider implementation** (core functionality)
2. **GUI integration** (user-facing)
3. **Testing edge cases** (error handling when Ollama is down)

Claude Code excels at all three if you break them into clear tasks.

---

## Bonus: Speed Tips

### Keyboard Shortcuts & Workflows
```bash
# Use aliases for common commands
alias cc="claude-code"
alias cctest="claude-code 'Run pytest and show any failures'"
alias ccfix="claude-code 'Fix the last error shown in terminal'"

# Chain commands
cc "Create Ollama.py" && cctest && git commit -m "Add Ollama provider"
```

### Quick Fixes
```bash
# For rapid iteration
cc "Quick fix: model list not updating" 
# vs lengthy explanation
```

---

Would you like me to elaborate on any specific aspect, or shall we start implementing the Ollama provider with these best practices in mind?