# 📁 PROJECT FILE REFERENCE

## Core System Files

### `rag_core.py` (2.0 KB)
**Purpose:** Token counting, smart truncation, and budget definitions
**Key Functions:**
- `count_tokens(text)` - Count exact token count using tiktoken (cl100k_base)
- `smart_truncate(text, budget, strategy)` - Truncate with two strategies:
  - `keep_start`: Preserve beginning (for instructions/facts)
  - `keep_end`: Preserve ending (for chat history/logs)
- `BUDGETS` dict - Hard constraints per section

**Dependencies:** `tiktoken` only

---

### `assembler.py` (6.8 KB)
**Purpose:** Context assembly, semantic retrieval, data orchestration
**Key Components:**
- `CV_DATA` - Mock knowledge base (10 documents)
- `bm25_score()` - BM25 relevance ranking algorithm
- `semantic_search()` - Retrieve top-k documents by relevance
- `build_context_window()` - Main assembly function:
  1. Instructions (255) - System prompt
  2. Memory (55) - Static facts
  3. Retrieval (550) - BM25 search results
  4. Tool Outputs (855) - System logs
  5. Goal (1,500) - Chat history with sliding window

**Dependencies:** `rag_core` module

---

### `app.py` (6.4 KB)
**Purpose:** Streamlit web dashboard interface
**Features:**
- Chat interface on left column
- Real-time metrics dashboard on right
- Token usage breakdown per section
- Budget status indicators (✅ OK / ⚠️ TRUNCATED)
- Context inspection expander
- Mock Ollama fallback (for offline testing)
- Ollama integration (when available)

**Configuration:**
- `OLLAMA_URL` - Endpoint for LLM (default: localhost:11434)
- `MODEL_NAME` - LLM model name (default: llama3)

**Dependencies:** `streamlit`, `requests`, `assembler`, `rag_core`

---

### `cli.py` (8.1 KB)
**Purpose:** Terminal-based interactive interface
**Features:**
- Interactive chat-like interface
- Real-time token metrics with progress bars
- Color-coded output (✅ green, ⚠️ yellow, ❌ red)
- Budget configuration display
- Retrieval results with BM25 scores
- Mock response generation
- Commands: `budget`, `demo`, `quit`

**Usage:**
```bash
python cli.py              # Interactive chat
python cli.py --budget     # Show budgets and exit
python cli.py --help       # Show help and exit
```

**Dependencies:** `assembler`, `rag_core`

---

## Test & Verification Files

### `test_demo.py` (11.8 KB)
**Purpose:** Comprehensive test suite with 6 demonstrations
**Demonstrations:**

1. **DEMO 1: Retrieval Corpus** - Lists all 10 CV documents with token counts
2. **DEMO 2: Token Counting** - Tests tiktoken accuracy on various texts
3. **DEMO 3: Truncation Strategies** - Shows keep_start vs keep_end behavior
4. **DEMO 4: Budget Overflow Handling** - Tests each section with 2-10x overflow:
   - Instructions: 341 → 255 tokens
   - Retrieval: 1,357 → 550 tokens
   - Goal: 3,020 → 1,500 tokens
   - Tool Outputs: 814 tokens (fits)
   - Memory: 101 → 55 tokens
5. **DEMO 5: Query Assembly** - 3 end-to-end queries
6. **DEMO 6: Budget Summary** - Configuration and allocation overview

**Run:** `python test_demo.py`

**Dependencies:** `assembler`, `rag_core`

---

### `verify_setup.py` (3.2 KB)
**Purpose:** System setup and dependency verification
**Checks:**
- Python version (3.8+)
- Required packages: tiktoken, streamlit, requests
- Core files: rag_core.py, assembler.py, app.py, cli.py, test_demo.py
- Provides installation assistance if needed

**Run:** `python verify_setup.py`

**Output:**
- ✅ ALL CHECKS PASSED - System is ready
- ❌ Error messages with remediation steps

---

## Documentation Files

### `README.md` (11.2 KB)
**Purpose:** Project overview, quick start, architecture
**Sections:**
- Assessment requirements met
- Quick start guide
- Architecture overview
- Budget structure and allocation
- Worked examples
- File reference
- Extension points

---

### `IMPLEMENTATION_GUIDE.md` (18.5 KB)
**Purpose:** Technical deep dive and implementation details
**Sections:**
- Quick start (3 interfaces)
- System architecture (5 layers)
- Token budget structure (5 sections)
- Core algorithms:
  - Token counting (tiktoken)
  - Smart truncation (2 strategies)
  - BM25 semantic retrieval
  - Context assembly
- Worked example (detailed walkthrough)
- Budget overflow scenarios
- Design principles
- File reference
- Assessment compliance checklist
- Extension points

---

### `COMPLETION_SUMMARY.md` (16.8 KB)
**Purpose:** Assessment compliance checklist and verification
**Sections:**
- Executive summary
- All 5 requirements with ✅ verification
- Architecture overview
- Technical implementation details
- File inventory
- Test coverage (6 demos)
- Key highlights
- Quick start verification
- Budget metrics
- Key learnings
- Compliance checklist

---

### `QUICKSTART_GUIDE.md` (8.0 KB)
**Purpose:** Fast-track usage guide for getting started
**Sections:**
- Assessment requirements checklist
- Step-by-step quick start (4 steps, ~7 minutes total)
- File inventory
- Test results summary
- Key features demonstrated
- What makes this special
- Advanced usage
- Performance metrics
- FAQ
- Learning outcomes

---

## Configuration Files

### `requirements.txt` (4 lines)
**Purpose:** Python package dependencies
**Contents:**
```
streamlit
tiktoken
requests
```

**Install:** `pip install -r requirements.txt`

---

## Usage Guide Summary

| Task | Command |
|------|---------|
| **Verify Setup** | `python verify_setup.py` |
| **Run Tests** | `python test_demo.py` |
| **Interactive CLI** | `python cli.py` |
| **Show Budgets** | `python cli.py --budget` |
| **Web Dashboard** | `python -m streamlit run app.py` |

---

## Directory Structure

```
Nyiko-chatbot/
├── README.md                    # Project overview
├── IMPLEMENTATION_GUIDE.md      # Technical details
├── COMPLETION_SUMMARY.md        # Assessment checklist
├── QUICKSTART_GUIDE.md          # Fast-track guide
├── FILE_REFERENCE.md            # This file
├── requirements.txt             # Dependencies
├── rag_core.py                  # Core logic (58 lines)
├── assembler.py                 # Assembly + retrieval (135 lines)
├── app.py                       # Streamlit UI (180 lines)
├── cli.py                       # Terminal UI (250 lines)
├── test_demo.py                 # Test suite (320 lines)
└── verify_setup.py              # Setup verification (150 lines)

Total: ~1,943 lines of code
Total: ~97 KB of documentation + code
```

---

## Quick Reference: What Each File Does

| File | Type | Purpose | When to Use |
|------|------|---------|------------|
| `rag_core.py` | Logic | Token counting & truncation | Core functionality |
| `assembler.py` | Logic | Assembly & retrieval | Core functionality |
| `app.py` | UI | Web dashboard | Visual exploration |
| `cli.py` | UI | Terminal interface | Command-line use |
| `test_demo.py` | Test | Comprehensive tests | Verification |
| `verify_setup.py` | Tool | Setup verification | First-time setup |
| `README.md` | Doc | Overview & quick start | Getting started |
| `IMPLEMENTATION_GUIDE.md` | Doc | Technical details | Deep understanding |
| `COMPLETION_SUMMARY.md` | Doc | Assessment checklist | Verification |
| `QUICKSTART_GUIDE.md` | Doc | Fast-track guide | Quick start |
| `FILE_REFERENCE.md` | Doc | This reference | Understanding structure |

---

## Dependencies Tree

```
app.py
├── streamlit
├── requests
├── assembler.py
│   ├── math
│   ├── collections
│   └── rag_core.py
│       └── tiktoken
└── rag_core.py
    └── tiktoken

cli.py
├── sys
├── assembler.py
│   └── rag_core.py
│       └── tiktoken
└── rag_core.py
    └── tiktoken

test_demo.py
├── assembler.py
│   └── rag_core.py
│       └── tiktoken
└── rag_core.py
    └── tiktoken
```

**External Dependencies:** Only 3
- `streamlit` - Web UI framework
- `tiktoken` - Token counter
- `requests` - HTTP client

---

## File Sizes

| File | Size | Lines |
|------|------|-------|
| rag_core.py | 2.0 KB | 58 |
| assembler.py | 6.8 KB | 135 |
| app.py | 6.4 KB | 180 |
| cli.py | 8.1 KB | 250 |
| test_demo.py | 11.8 KB | 320 |
| verify_setup.py | 3.2 KB | 150 |
| README.md | 11.2 KB | 350 |
| IMPLEMENTATION_GUIDE.md | 18.5 KB | 450 |
| COMPLETION_SUMMARY.md | 16.8 KB | 410 |
| QUICKSTART_GUIDE.md | 8.0 KB | 250 |
| FILE_REFERENCE.md | 6.5 KB | 280 |
| **Total** | **~99 KB** | **~2,633** |

---

## Getting Started (First Time)

1. **Verify Setup** (1 min)
   ```bash
   python verify_setup.py
   ```

2. **Run Tests** (2 min)
   ```bash
   python test_demo.py
   ```

3. **Try CLI** (3 min)
   ```bash
   python cli.py
   ```

4. **Try Web Dashboard** (1 min)
   ```bash
   python -m streamlit run app.py
   ```

**Total time:** ~7 minutes

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: tiktoken` | Run `python verify_setup.py` |
| `streamlit: not recognized` | Use `python -m streamlit run app.py` |
| Tests won't run | Check Python version: `python --version` (need 3.8+) |
| Port 8501 already in use | Kill existing Streamlit: `lsof -ti :8501 \| xargs kill -9` |

---

*Created: January 12, 2026*  
*Last Updated: January 12, 2026*  
*Status: Complete & Verified ✅*
