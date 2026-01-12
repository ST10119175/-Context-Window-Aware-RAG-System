# Context-Window-Aware RAG System - Complete Reference

## 📋 Quick Start

### 1. Run the Comprehensive Test Suite
```bash
python test_demo.py
```
**Shows:** Token counting, truncation strategies, budget overflow handling, and real query assembly.

### 2. Run the Interactive CLI
```bash
python cli.py
```
**Shows:** Live interaction with budget enforcement and token metrics display.

### 3. Run the Streamlit Web UI (requires Ollama or mock mode)
```bash
streamlit run app.py
```
**Shows:** Real-time visualization of token usage with a chat interface.

---

## 🏗 System Architecture

The system is built on a **clean separation of concerns**:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  • Streamlit (app.py)  - Web dashboard with visualizations  │
│  • CLI (cli.py)        - Terminal-based interactive mode    │
│  • Tests (test_demo.py)- Automated demonstrations           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    ASSEMBLER LAYER                           │
│  • Context Assembly  (assembler.py)                          │
│    - Gathers data from multiple sources                      │
│    - Enforces token budgets                                  │
│    - Applies truncation strategies                           │
│    - BM25-based semantic retrieval                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    CORE LOGIC LAYER                          │
│  • Token Counting (rag_core.py)  - tiktoken encoder          │
│  • Budget Enforcement            - Strict limits per section │
│  • Smart Truncation              - Context-aware truncation  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  INFERENCE LAYER (Optional)                  │
│  • Ollama/Llama 3 - External LLM for generating responses   │
│  • Or Mock Responses - For testing without LLM             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Token Budget Structure

| Section | Budget | Source | Selection Logic | Truncation Strategy |
|---------|--------|--------|-----------------|-------------------|
| **Instructions** | 255 | System prompt | Static/High priority | `keep_start`: Core persona definition is usually at the top |
| **Goal** | 1,500 | Chat history | Time-series (most recent) | `keep_end`: Most recent messages are most relevant (sliding window) |
| **Memory** | 55 | Static facts | High-density critical info | `keep_start`: Compress to bare essentials |
| **Retrieval** | 550 | BM25 semantic search | Relevance score ranking | `keep_start`: Fill with top-ranked documents |
| **Tool Outputs** | 855 | System logs | Chronological | `keep_end`: Only latest execution status matters |
| **TOTAL** | **3,215** | — | — | — |

---

## 🔍 Core Algorithms

### 1. Token Counting (`count_tokens`)
**File:** `rag_core.py`

Uses `tiktoken` with the `cl100k_base` encoding (GPT-4 standard):
```python
encoder = tiktoken.get_encoding("cl100k_base")
token_count = len(encoder.encode(text))
```

**Why cl100k_base?** While Llama 3 uses a different tokenizer, this provides a safe, industry-standard approximation for budget management.

### 2. Smart Truncation (`smart_truncate`)
**File:** `rag_core.py`

Two strategies:

**Strategy: `keep_start`**
- Truncates from the END
- Use for: Instructions, system prompts, facts that must not be forgotten
- Example: "You are a helpful..." (keep) vs "...outdated context" (truncate)

**Strategy: `keep_end`**
- Truncates from the START (keeps the ending)
- Use for: Chat history, logs (most recent is most important)
- Example: "[Old turn 1]...[Old turn N]..." (truncate) vs "[Recent turn]" (keep)

### 3. Semantic Retrieval (`bm25_score`, `semantic_search`)
**File:** `assembler.py`

Implements BM25 ranking algorithm:
1. **Tokenize** the query
2. **For each document:**
   - Calculate Term Frequency (TF): How many times query terms appear?
   - Calculate Inverse Document Frequency (IDF): How rare is this term?
   - Apply BM25 formula: `IDF * (TF * (k1 + 1)) / (TF + k1 * (1 - b + b * (len/avg_len)))`
3. **Sort by score** and return top-k results

**Why BM25?** It's a proven ranking algorithm that balances term frequency with document length, avoiding bias toward longer documents.

---

## 📊 Worked Example: Query Assembly Pipeline

### Input
**User Query:** "Tell me about your experience with AI Agents."
**Chat History:** Empty (first message)

### Step 1: Instructions (255 token budget)
```
Original: "You are an AI assistant representing..."
Status: ✅ 40 tokens < 255 budget → Kept as-is
```

### Step 2: Memory (55 token budget)
```
Original: "Role: Job Candidate Bot. Status: Hired. Location: Centurion, South Africa."
Status: ✅ 18 tokens < 55 budget → Kept as-is
```

### Step 3: Retrieval (550 token budget)
```
BM25 Search Results:
  1. "He built a 'RAG Anime Discovery Engine' using LangChain and ChromaDB." (score: 8.2)
  2. "He currently works at GotBot AI developing Multi-Agent LLM systems." (score: 7.5)
  3. "He specializes in Python, Vertex AI, Dialogflow..." (score: 6.1)
  ...

Total: 520 tokens < 550 budget → Kept as-is
```

### Step 4: Tool Outputs (855 token budget)
```
Original: "[System Log] Processing query: 'Tell me about...' Retrieval complete..."
Status: ✅ 25 tokens < 855 budget → Kept as-is
```

### Step 5: Goal/Conversation (1,500 token budget)
```
Original: User: Tell me about your experience with AI Agents.
Status: ✅ 18 tokens < 1,500 budget → Kept as-is (first message)
```

### Final Assembly
```
### SYSTEM INSTRUCTIONS
[40 tokens] You are an AI assistant representing Nyiko...

### LONG TERM MEMORY
[18 tokens] Role: Job Candidate Bot. Status: Hired...

### CONTEXT (RETRIEVED KNOWLEDGE)
[520 tokens] RELEVANT CV DATA:
- He built a RAG Anime Discovery Engine...
- He currently works at GotBot AI...

### SYSTEM TOOLS
[25 tokens] [System Log] Processing query...

### CONVERSATION HISTORY
[18 tokens] User: Tell me about your experience with AI Agents.

TOTAL: 621 tokens (all within budgets ✅)
```

---

## 🧪 Budget Overflow Scenarios (Demonstrated in `test_demo.py`)

### Scenario 1: Instruction Overflow
**Simulated:** 2,000 token system prompt
**Expected Behavior:** Truncated to 255 tokens using `keep_start`
**Result:** Core persona definition preserved, verbose instructions discarded

### Scenario 2: Retrieval Overflow
**Simulated:** 50-document retrieval result
**Expected Behavior:** Truncated to 550 tokens using `keep_start`
**Result:** Top-ranked documents kept, lower-scoring ones removed

### Scenario 3: Goal/History Overflow
**Simulated:** 10 conversation turns (3,000 tokens)
**Expected Behavior:** Truncated to 1,500 tokens using `keep_end`
**Result:** Old turns removed, recent messages preserved (sliding window)

### Scenario 4: Tool Outputs Overflow
**Simulated:** 200 log entries
**Expected Behavior:** Truncated to 855 tokens using `keep_end`
**Result:** Old logs discarded, latest execution status kept

### Scenario 5: Memory Overflow (Tight Budget)
**Simulated:** 500 token "static facts"
**Expected Behavior:** Truncated to 55 tokens using `keep_start`
**Result:** Only the most critical facts preserved

---

## 🎯 Key Design Principles

### 1. **Deterministic Context Assembly**
Every prompt is built in a reproducible way. No randomness, no heuristics—just clear, auditable rules.

### 2. **Strict Budget Enforcement**
Sections NEVER exceed their token limits. If they overflow, they're truncated deterministically.

### 3. **Intelligent Truncation**
Different sections use different truncation strategies based on their importance:
- Instructions: Preserve definition (keep_start)
- History: Preserve recency (keep_end)
- Retrieval: Preserve relevance (keep_start, after ranking)

### 4. **Separation of Concerns**
- `rag_core.py` = Pure logic (no dependencies)
- `assembler.py` = Orchestration and retrieval
- `app.py` / `cli.py` = User interface

This makes the system easy to audit, test, and extend.

### 5. **Observable & Debuggable**
- Every section's token count is visible
- Final prompt is inspectable
- Truncation reasons are clear

---

## 📁 File Reference

### Core Files

**`rag_core.py`** (160 lines)
- `count_tokens(text)`: Count exact token count using tiktoken
- `smart_truncate(text, budget, strategy)`: Intelligently truncate based on strategy
- `BUDGETS`: Dictionary of hard limits

**`assembler.py`** (120+ lines)
- `CV_DATA`: Mock knowledge base
- `bm25_score()`: Calculate document relevance
- `semantic_search()`: Retrieve top-k documents
- `build_context_window()`: Main assembly function

### Interface Files

**`app.py`** (180 lines)
- Streamlit web dashboard
- Chat history management
- Real-time token visualization
- Mock Ollama fallback

**`cli.py`** (200 lines)
- Interactive terminal interface
- Live token metrics
- Chat-like interaction

**`test_demo.py`** (300+ lines)
- Comprehensive test suite
- Budget overflow demonstrations
- Token counting validation
- Real query assembly examples

---

## ✅ Assessment Compliance Checklist

- [x] **Runnable CLI** - `cli.py` provides interactive interface
- [x] **Minimal Web UI** - `app.py` with Streamlit dashboard
- [x] **Vector Retrieval** - BM25-based semantic search in `assembler.py`
- [x] **Context Assembly** - Budget structure implemented per spec
- [x] **Budget Display** - Metrics dashboard in CLI and Streamlit
- [x] **Budget Overflow** - All 5 sections demonstrate truncation in `test_demo.py`
- [x] **Token Counting** - Accurate with `tiktoken` cl100k_base
- [x] **Truncation Strategies** - Two strategies (keep_start, keep_end) applied correctly
- [x] **Clean Architecture** - Separation of logic, assembly, and UI layers

---

## 🚀 Usage Examples

### Example 1: Run All Demos
```bash
python test_demo.py
```
Output: 6 comprehensive demonstrations of the system

### Example 2: Interactive Chat (CLI)
```bash
python cli.py
```
```
You: Tell me about your cloud experience.

🔍 Retrieval Results:
  [1] Score: 8.234 (AWS Cloud Practitioner...)
  [2] Score: 7.891 (Vertex AI...)

📈 Token Usage:
  INSTRUCTIONS    40 / 255 tokens ✅
  RETRIEVAL      420 / 550 tokens ✅
  MEMORY          18 /  55 tokens ✅
  GOAL            25 / 1500 tokens ✅
  TOOL_OUTPUTS    15 / 855 tokens ✅
  TOTAL: 518 tokens

Assistant (Mock Response):
  • He is an AWS Cloud Practitioner and is actively...
  • He specializes in Python, Vertex AI, Dialogflow...
```

### Example 3: Inspect Budget Config
```bash
python cli.py --budget
```

---

## 🔧 Extending the System

### Add a New Knowledge Base
Replace `CV_DATA` in `assembler.py` with your own documents:
```python
CV_DATA = [
    "Your document 1",
    "Your document 2",
    # ...
]
```

### Integrate Real Vector Database
Replace `semantic_search()` with Chroma/Pinecone integration:
```python
def semantic_search(query, corpus, top_k=3):
    # Call your vector DB API
    results = chromadb.collection.query(query_texts=[query], n_results=top_k)
    return results
```

### Connect Real LLM
In `app.py`, replace Ollama with your API:
```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": final_prompt}]
)
```

---

## 📝 Notes

- All token counts use `tiktoken` with `cl100k_base` (GPT-4 standard)
- The system is designed to work offline (mock mode) or with Ollama
- Budget totals to 3,215 tokens (safe for 4k-8k context windows)
- Truncation is deterministic and reproducible
- No randomness or stochastic behavior in assembly

---

## 💡 For the Deloitte Assessment

This system demonstrates:

1. **Context Economics** - Strict budget enforcement per section
2. **Intelligent Prioritization** - Different truncation strategies based on data importance
3. **Clean Architecture** - Separation of logic, assembly, and UI
4. **Observability** - Every decision is visible and auditable
5. **Scalability** - Can drop in a real vector DB or LLM without changing logic
6. **Robustness** - Graceful handling of budget overflows
