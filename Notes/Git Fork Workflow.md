# Git Fork Workflow - Complete Guide

## Your Setup
- **upstream**: Original repo (xtekky/gpt4free) - read-only
- **origin**: Your fork (HardCodedLife/gpt4free) - you control this
- **main**: Your main branch (stays synced with upstream)
- **ollama-integration**: Your feature branch (your custom work)

---

## Daily Workflow

### 1. Start Your Day - Sync with Upstream

```bash
# Make sure you're on main branch
git switch main

# Fetch latest changes from upstream (doesn't modify your files yet)
git fetch upstream main

# Merge upstream changes into your main
git merge upstream/main --no-ff

# Push updated main to your fork
git push origin main
```

**What this does:**
- `git switch main` - Moves you to the main branch
- `git fetch upstream main` - Downloads new commits from original repo, but doesn't apply them yet
- `git merge upstream/main --no-ff` - Combines upstream changes with yours, creates a merge commit
- `git push origin main` - Uploads your updated main to your GitHub fork

---

### 2. Work on Your Features

```bash
# Switch to your feature branch
git switch ollama-integration

# Update it with latest main (includes upstream changes)
git merge main

# Now work on your code...
# ... make changes ...

# Check what you changed
git status
git diff

# Stage your changes
git add .
# Or stage specific files:
git add path/to/file.py

# Commit your changes
git commit -m "Add ollama integration feature"

# Push to your fork
git push origin ollama-integration
```

**What this does:**
- `git switch ollama-integration` - Moves to your feature branch
- `git merge main` - Brings upstream updates into your feature branch
- `git status` - Shows modified/new/deleted files
- `git diff` - Shows exact changes you made (line by line)
- `git add` - Stages files for commit (prepares them)
- `git commit` - Saves your changes with a message
- `git push origin ollama-integration` - Uploads your feature to GitHub

---

### 3. Check Your Work (Anytime)

```bash
# See which branch you're on
git branch

# See all remotes
git remote -v

# See commit history
git log --oneline -10

# See what changed between branches
git diff main..ollama-integration

# See if you're ahead/behind remote
git status
```

---

## Common Scenarios

### Scenario A: Upstream Released New Updates

```bash
git switch main
git fetch upstream main
git merge upstream/main --no-ff
git push origin main

# Update your feature branch too
git switch ollama-integration
git merge main
git push origin ollama-integration
```

### Scenario B: You Made Changes on Wrong Branch

```bash
# If changes aren't committed yet
git stash                    # Save changes temporarily
git switch ollama-integration  # Switch to correct branch
git stash pop                # Apply saved changes here
```

### Scenario C: Want to See What's New in Upstream

```bash
git fetch upstream main
git log main..upstream/main  # See commits you don't have
```

### Scenario D: Merge Conflicts (Files Changed in Both Places)

```bash
git merge main
# CONFLICT! Git will tell you which files

# Open the conflicting files, look for:
<<<<<<< HEAD
your changes
=======
upstream changes
>>>>>>> main

# Edit to keep what you want, remove the markers
# Then:
git add path/to/resolved/file.py
git commit -m "Resolve merge conflict"
```

---

## Weekly Routine (Recommended)

**Monday morning:**
```bash
git switch main
git fetch upstream main
git merge upstream/main --no-ff
git push origin main
git switch ollama-integration
git merge main
git push origin ollama-integration
```

**During the week:**
```bash
# Work on ollama-integration branch
git add .
git commit -m "Your changes"
git push origin ollama-integration
```

**Before weekend:**
```bash
# Make sure everything is pushed
git status
git push origin ollama-integration
```

---

## Important Rules

1. **Never work directly on `main`** - Keep it clean for syncing with upstream
2. **Always work on `ollama-integration`** (or other feature branches)
3. **Sync `main` first, then merge into feature branch** - Keeps things organized
4. **Commit often with clear messages** - Easier to track and undo if needed
5. **Push regularly** - Backs up your work to GitHub

---

## Quick Reference

| Command | What It Does |
|---------|--------------|
| `git switch <branch>` | Change to another branch |
| `git fetch upstream main` | Download upstream changes (doesn't apply them) |
| `git merge <branch>` | Combine another branch into current branch |
| `git push origin <branch>` | Upload your branch to GitHub |
| `git status` | See what's changed |
| `git log` | See commit history |
| `git diff` | See exact changes |
| `git add <file>` | Stage file for commit |
| `git commit -m "msg"` | Save staged changes |
| `git stash` | Temporarily save uncommitted changes |

---

## Visual Flow

```
upstream/main (original repo)
    ↓ (fetch + merge)
origin/main (your fork)
    ↓ (merge)
ollama-integration (your work)
    ↓ (push)
origin/ollama-integration (your fork on GitHub)
```