# System Architecture & Data Flow Diagrams

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      USER INTERACTION LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐     │
│  │   CLI.py     │  │   app.py     │  │   test_demo.py       │     │
│  │  (Terminal)  │  │ (Streamlit)  │  │  (Automated Tests)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘     │
│         │                 │                     │                  │
│         └─────────────────┼─────────────────────┘                  │
│                           │                                         │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CONTEXT ASSEMBLY LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│                      assembler.py                                   │
│                                                                     │
│  User Query ──┬──────────────────────────────────────────────┐    │
│               │                                              │     │
│               ▼                                              │     │
│      ┌──────────────────────────────────────┐              │     │
│      │  BM25 Semantic Search                │              │     │
│      │  ├─ Tokenize query                   │              │     │
│      │  ├─ Score against CV_DATA            │              │     │
│      │  └─ Return top-k results by relevance│              │     │
│      └──────┬───────────────────────────────┘              │     │
│             │                                              │     │
│             ▼                                              │     │
│  ┌─────────────────────────────────────────────────────┐  │     │
│  │  Gather Data from 5 Sources                        │  │     │
│  ├─ Instructions (System prompt) ─────────────┐       │  │     │
│  ├─ Memory (Static facts) ──────────────────┐ │       │  │     │
│  ├─ Retrieval (Ranked documents) ──────────┤─┼───┐   │  │     │
│  ├─ Goal (Chat history) ────────────────────┤ │   │   │  │     │
│  └─ Tool Outputs (System logs) ─────────────┘ │   │   │  │     │
│                                               │   │   │   │     │
│  Assemble these into build_context_window()   │   │   │   │     │
│  returns: (final_prompt, usage_report)        └───┘   │   │     │
│                                                       │   │     │
│  usage_report = {                                    │   │     │
│    'instructions': [content],                       │   │     │
│    'memory': [content],                            │   │     │
│    'retrieval': [content],          ◄──────────────┘   │     │
│    'goal': [content],                                  │     │
│    'tool_outputs': [content]                           │     │
│  }                                                      │     │
│                                                        │     │
└────────────────────────────────────────────────────────┼─────┘
                                                         │
                            ┌────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CORE LOGIC LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                        rag_core.py                                  │
│                                                                     │
│  For each section in usage_report:                                 │
│                                                                     │
│      ┌─────────────────────────────────────────┐                   │
│      │ count_tokens(content)                   │                   │
│      │ ├─ Use tiktoken.get_encoding("cl100k")  │                   │
│      │ ├─ tokens = encoder.encode(content)     │                   │
│      │ └─ return len(tokens)                   │                   │
│      └─────┬───────────────────────────────────┘                   │
│            │                                                        │
│            ▼                                                        │
│      ┌─────────────────────────────────────────┐                   │
│      │ smart_truncate(content, budget,         │                   │
│      │                strategy)                │                   │
│      │                                         │                   │
│      │ if tokens <= budget:                    │                   │
│      │   return content (no truncation)        │                   │
│      │                                         │                   │
│      │ if strategy == "keep_start":            │                   │
│      │   truncated = tokens[:budget]           │                   │
│      │   return decoder(truncated)             │                   │
│      │                                         │                   │
│      │ elif strategy == "keep_end":            │                   │
│      │   truncated = tokens[-budget:]          │                   │
│      │   return decoder(truncated)             │                   │
│      └─────┬───────────────────────────────────┘                   │
│            │                                                        │
│            ▼                                                        │
│      ┌─────────────────────────────────────────┐                   │
│      │ Enforce Budget Constraints              │                   │
│      │ BUDGETS = {                             │                   │
│      │   'instructions': 255,    (7.9%)        │                   │
│      │   'goal': 1500,           (46.7%)       │                   │
│      │   'memory': 55,           (1.7%)        │                   │
│      │   'retrieval': 550,       (17.1%)       │                   │
│      │   'tool_outputs': 855     (26.6%)       │                   │
│      │ }                                       │                   │
│      │ TOTAL: 3215 tokens                      │                   │
│      └─────────────────────────────────────────┘                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FINAL OUTPUT                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  final_prompt = """                                                 │
│  ### SYSTEM INSTRUCTIONS                                            │
│  [Truncated to 255 tokens via keep_start]                          │
│                                                                     │
│  ### LONG TERM MEMORY                                               │
│  [Truncated to 55 tokens via keep_start]                           │
│                                                                     │
│  ### CONTEXT (RETRIEVED KNOWLEDGE)                                  │
│  [Truncated to 550 tokens via keep_start]                          │
│                                                                     │
│  ### SYSTEM TOOLS                                                   │
│  [Truncated to 855 tokens via keep_end]                            │
│                                                                     │
│  ### CONVERSATION HISTORY                                           │
│  [Truncated to 1500 tokens via keep_end]                           │
│  """                                                                │
│                                                                     │
│  Total Context Size: [X] tokens (checked ≤ 3215)  ✅              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              INFERENCE ENGINE (Optional)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────┐      ┌──────────────────────────┐   │
│  │  If Ollama Available:    │      │  If Ollama Unavailable:  │   │
│  │                          │      │                          │   │
│  │  POST to Ollama          │      │  Generate Mock Response  │   │
│  │  /api/generate           │      │  (show budget logic      │   │
│  │  ├─ model: llama3        │      │   worked!)               │   │
│  │  ├─ prompt: final_prompt │      │                          │   │
│  │  └─ stream: false        │      │  Graceful Fallback ✓     │   │
│  │                          │      │                          │   │
│  │  LLM Response            │      │  Demonstration Response  │   │
│  └──────────────────────────┘      └──────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Budget Allocation Flow

```
Total Context Window: 4096-8192 tokens
│
├─ System Overhead: ~500-1000 tokens
│  (Formatting, padding, LLM internal buffers)
│
└─ Available Budget: 3215 tokens (ALLOCATED)
   │
   ├─► Instructions (255 tokens)
   │   ├─ What: System prompt
   │   ├─ Strategy: keep_start (preserve definition)
   │   ├─ Example: "You are an AI assistant..."
   │   └─ Status: [████░░░░░░░░░░░░░░░░░░░░░░]  7.9%
   │
   ├─► Memory (55 tokens)
   │   ├─ What: Static facts
   │   ├─ Strategy: keep_start (compress to essentials)
   │   ├─ Example: "Role: Candidate Bot"
   │   └─ Status: [██░░░░░░░░░░░░░░░░░░░░░░░░░]  1.7%
   │
   ├─► Retrieval (550 tokens)
   │   ├─ What: Dynamic knowledge (ranked by BM25)
   │   ├─ Strategy: keep_start (preserve top-ranked)
   │   ├─ Example: "He has AI expertise..."
   │   └─ Status: [████████░░░░░░░░░░░░░░░░░░░] 17.1%
   │
   ├─► Tool Outputs (855 tokens)
   │   ├─ What: System logs
   │   ├─ Strategy: keep_end (latest status only)
   │   ├─ Example: "[Log] Retrieval complete..."
   │   └─ Status: [█████████████░░░░░░░░░░░░░░] 26.6%
   │
   └─► Goal/History (1500 tokens)
       ├─ What: Chat conversation
       ├─ Strategy: keep_end (sliding window)
       ├─ Example: "User: Tell me about AI..."
       └─ Status: [███████████████████████░░░░] 46.7%
```

---

## 3. Context Assembly Pipeline

```
Input: User Query + Chat History
│
├─ Parse & Tokenize
│  user_query = "Tell me about your AI experience."
│  tokens = 10
│
├─ Step 1: Gather Instructions
│  └─ Load system prompt → 45 tokens
│
├─ Step 2: Gather Memory  
│  └─ Load static facts → 18 tokens
│
├─ Step 3: Semantic Retrieval
│  ├─ BM25 score all documents
│  ├─ Rank by relevance
│  ├─ Top results:
│  │  [1] "He built a RAG..." (8.2 score)
│  │  [2] "He works at GotBot..." (7.5 score)
│  │  [3] "He specializes in..." (6.1 score)
│  └─ Combined: 140 tokens
│
├─ Step 4: Gather Tool Outputs
│  └─ Latest logs → 25 tokens
│
├─ Step 5: Gather Goal/History
│  └─ Chat history (sliding) → 10 tokens
│
├─ Enforce Budgets
│  instructions: 45 ≤ 255 ✅ (keep as-is)
│  memory: 18 ≤ 55 ✅ (keep as-is)
│  retrieval: 140 ≤ 550 ✅ (keep as-is)
│  tool_outputs: 25 ≤ 855 ✅ (keep as-is)
│  goal: 10 ≤ 1500 ✅ (keep as-is)
│
├─ Assemble Final Prompt
│  ### SYSTEM INSTRUCTIONS
│  [45 tokens]
│  
│  ### LONG TERM MEMORY
│  [18 tokens]
│  
│  ### CONTEXT
│  [140 tokens]
│  
│  ### SYSTEM TOOLS
│  [25 tokens]
│  
│  ### CONVERSATION HISTORY
│  [10 tokens]
│
└─ Output: final_prompt (238 tokens total)
   Usage Report for Dashboard:
   - instructions: 45/255 ✅
   - memory: 18/55 ✅
   - retrieval: 140/550 ✅
   - tool_outputs: 25/855 ✅
   - goal: 10/1500 ✅
```

---

## 4. Budget Overflow Scenario

```
Input: Very Long System Prompt (341 tokens)
Budget: Instructions = 255 tokens
│
├─ count_tokens(prompt)
│  └─ Result: 341 tokens ⚠️ EXCEEDS BUDGET
│
├─ smart_truncate(prompt, 255, "keep_start")
│  ├─ Encode full text: 341 tokens
│  ├─ Slice tokens[:255]: First 255 tokens
│  ├─ Keep: "You are an AI assistant representing..." ✓
│  ├─ Remove: "...and provide extremely detailed..." ✗
│  └─ Decode back to text
│
└─ Output: 255 tokens ✅ FITS BUDGET
   Truncated Content preserved core definition
   Status: ✅ OK (was ⚠️ TRUNCATED, now fixed)
```

---

## 5. BM25 Relevance Scoring

```
Query: "Tell me about your AI experience"

For each document in CV_DATA:
│
├─ Document 1: "Nyiko is an AI Engineer..."
│  ├─ Tokenize: ["nyiko", "is", "an", "ai", "engineer"]
│  ├─ TF (term frequency):
│  │  - "ai": 1 (appears once)
│  │  - "engineer": 1
│  ├─ IDF (inverse document frequency):
│  │  - "ai": appears in 3 docs → IDF = high
│  │  - "engineer": appears in 2 docs → IDF = very high
│  ├─ Doc length: 12 words (slightly longer)
│  ├─ BM25 formula: IDF * (TF*1.5) / (TF + k1*(1-b + b*len/avg))
│  └─ Score: 2.34 ✓
│
├─ Document 2: "He built a RAG Anime Engine..."
│  ├─ Tokenize: ["he", "built", "rag", "anime", "engine"]
│  ├─ TF: No "ai" (0), "engine": 1
│  ├─ IDF: "engine" is rare → high
│  └─ Score: 0.89
│
├─ Document 3: "He is fluent in English..."
│  ├─ Tokenize: ["he", "is", "fluent", "in", "english"]
│  ├─ TF: All terms match minimally
│  ├─ IDF: All terms are common
│  └─ Score: 0.12
│
└─ RANKING (by score):
   [1] Doc 1 (2.34) ← Selected
   [2] Doc 2 (0.89) ← Selected
   [3] Doc 3 (0.12) ← Selected
   ...
```

---

## 6. User Interface Workflows

### CLI Workflow
```
START
  │
  ├─ Display Welcome Banner
  │  └─ Show budget configuration
  │
  ├─ Prompt: "You: "
  │
  ├─ Process Input
  │  ├─ If "budget" → Show configuration
  │  ├─ If "demo" → Show all documents
  │  ├─ If "quit" → Exit
  │  └─ Otherwise → Process as query
  │
  ├─ On Query
  │  ├─ Show retrieval results with BM25 scores
  │  ├─ Display token metrics per section
  │  ├─ Option to inspect final context
  │  ├─ Show mock response
  │  └─ Update history
  │
  └─ Loop
```

### Web UI Workflow
```
START (Streamlit)
  │
  ├─ Display Header
  │
  ├─ Left Column (Chat)
  │  ├─ Display message history
  │  ├─ Input box: "Ask about Nyiko's experience..."
  │  └─ On Submit:
  │     ├─ Display user message
  │     ├─ Call Ollama (or mock)
  │     ├─ Display AI response
  │     └─ Update history
  │
  └─ Right Column (Dashboard)
     ├─ Display metrics if query exists
     │  ├─ Instructions: X / 255 [progress bar]
     │  ├─ Retrieval: X / 550 [progress bar]
     │  ├─ Memory: X / 55 [progress bar]
     │  ├─ Goal: X / 1500 [progress bar]
     │  └─ Tool Outputs: X / 855 [progress bar]
     │
     ├─ Show total context size
     ├─ Warn if truncation occurred
     ├─ Expander: View full assembled context
     └─ Expander: View retrieval details
```

---

## 7. Data Flow Summary

```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Parse & Tokenize    │
└──────┬───────────────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌────────────────┐                ┌──────────────────┐
│ System Prompt  │                │ Retrieval Search │
└────────┬───────┘                │ (BM25 Ranking)   │
         │                        └────────┬─────────┘
         │                                 │
         ├─► count_tokens()               │
         │   └─ 45 tokens                 │
         │                                 │
         ├─► smart_truncate(,255,keep_s)  │
         │   └─ 45 tokens < 255 ✓         │
         │                                 │
         │   ┌────────────────────────────┘
         │   │
         ▼   ▼
    ┌─────────────────────────────┐
    │  Other Sections             │
    │  (Memory, Tools, History)   │
    └──────────┬──────────────────┘
               │
               ├─ All sections counted & truncated
               │
               ▼
    ┌─────────────────────────────┐
    │  Verify Budget Constraints  │
    │  Total ≤ 3215? ✅           │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Assemble Final Prompt      │
    │  With Labels & Structure    │
    └──────────┬──────────────────┘
               │
               ├─► To UI Dashboard (metrics)
               │
               ├─► To LLM (final_prompt)
               │
               └─► To Storage (logs)
```

---

This visual documentation helps understand:
- How components interact
- What data flows through which sections
- How budgets are enforced
- What happens during overflow
- How truncation strategies work
- The complete user journey
