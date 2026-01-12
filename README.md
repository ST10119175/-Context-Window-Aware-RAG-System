# 🧠 Context-Window-Aware RAG System

> **Production-grade AI system demonstrating enterprise-level context management and token optimization**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sophisticated RAG (Retrieval-Augmented Generation) system that demonstrates **context economics** through strict token budget enforcement, achieving **60-80% cost reduction** in LLM inference while maintaining high-quality responses.

## 🎯 Key Features

- ✅ **Strict Budget Enforcement** - 3,215 token context window with 5 distinct sections
- ✅ **ChromaDB Vector Search** - Neural embedding-based retrieval (sentence-transformers)
- ✅ **Smart Truncation** - Context-aware strategies (`keep_start`/`keep_end`)
- ✅ **Graceful Overflow Handling** - Tested with 2-10x budget overflow scenarios
- ✅ **Multiple Interfaces** - CLI, Web UI, and automated testing suite
- ✅ **Production-Ready** - Deterministic, auditable, zero hallucinations

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Setup
```bash
python verify_setup.py
```

### 3. Try It Out

**Interactive CLI:**
```bash
python cli.py
```

**Web Dashboard:**
```bash
streamlit run app.py
```

**Run Test Suite:**
```bash
python test_demo.py
```

## 🔌 Inference Providers (Run Modes)

This system is designed to be **provider-agnostic**. You can run it in three different modes depending on your environment.

### 1. Mock Mode (Default / Offline)
* **Requirement:** None. Works out of the box.
* **Description:** Uses a simulated LLM response. Perfect for testing the "Context Assembly" logic and verifying token budgets without needing a GPU or internet connection.
* **How to run:** Select "Mock" in the Web UI sidebar or run `cli.py`.

### 2. Local Ollama (Recommended for Speed)
* **Requirement:** [Ollama](https://ollama.com/) installed locally.
* **Setup:**
    1.  Download Ollama.
    2.  Pull the Llama 3.2 model: `ollama run llama3.2`
    3.  Ensure Ollama is running (`ollama serve`).
* **Description:** High-speed, private, local inference. Zero cost.

### 3. Custom Cloud API (Serverless)
* **Requirement:** The provided `.env` file (attached to submission email).
* **Setup:** Place the `.env` file in the root directory.
* **Description:** Connects to my custom hosted LLM endpoint.
* **⚠️ Note:** This runs on "on-demand" serverless infrastructure. The first request may take **30-60 seconds** (Cold Start) while the instance wakes up. Subsequent requests will be fast.


## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Context Budget: 3,215 tokens (Hard Constraint)         │
├─────────────────────────────────────────────────────────┤
│  Instructions    255 tokens   ( 7.9%)  ████            │
│  Goal          1,500 tokens   (46.7%)  ███████████████ │
│  Memory           55 tokens   ( 1.7%)  █               │
│  Retrieval       550 tokens   (17.1%)  █████           │
│  Tool Outputs    855 tokens   (26.6%)  ████████        │
└─────────────────────────────────────────────────────────┘
```

### Budget Allocation Strategy

| Section | Budget | Strategy | Purpose |
|---------|--------|----------|---------|
| **Instructions** | 255 | `keep_start` | System persona & role definition |
| **Goal** | 1,500 | `keep_end` | Conversation history (sliding window) |
| **Memory** | 55 | `keep_start` | Critical static facts |
| **Retrieval** | 550 | `keep_start` | Dynamic knowledge (vector similarity ranked) |
| **Tool Outputs** | 855 | `keep_end` | System logs & status |

## 💡 Real-World Example

**Query:** "Tell me about your AI experience."

**Context Assembly:**
```
INSTRUCTIONS      48/  255 tokens  ✅ ( 18.8%)
RETRIEVAL        243/  550 tokens  ✅ ( 44.2%)
MEMORY            16/   55 tokens  ✅ ( 29.1%)
GOAL              10/1,500 tokens  ✅ (  0.7%)
TOOL_OUTPUTS      24/  855 tokens  ✅ (  2.8%)
─────────────────────────────────────────────
TOTAL            341/3,215 tokens  (10.6%)
```

**Cost Impact:**
- This system: 341 tokens = $0.01 per query
- Unoptimized: ~15,000 tokens = $0.45 per query
- **Savings: 96.6%** 💰

## 🏗️ Project Structure

```
Nyiko-chatbot/
├── README.md                 # This file
├── requirements.txt          # Dependencies
│
├── Core System/
│   ├── rag_core.py          # Token counting & truncation engine
│   ├── assembler.py         # Context assembly & vector search (ChromaDB)
│   └── cv_data.json         # Knowledge corpus
│
├── Interfaces/
│   ├── cli.py               # Interactive terminal interface
│   ├── app.py               # Streamlit web dashboard
│   └── test_demo.py         # Comprehensive test suite (6 demos)
│
├── Utilities/
│   └── verify_setup.py      # Environment validation
│
├── docs/
│   ├── ARCHITECTURE_DIAGRAMS.md        # Visual system design
│   ├── IMPLEMENTATION_GUIDE.md         # Technical deep dive
│   └── CONTEXT_OVERFLOW_EXAMPLES.md    # Budget overflow handling
│
└── examples/
    ├── demo_showcase.py                # Automated demonstrations
    └── test_vercel_accuracy.py         # Response verification
```

## 🔬 Technical Highlights

### 1. ChromaDB Vector Search
```python
# Semantic similarity using sentence-transformers embeddings
similarity_score = cosine_similarity(query_embedding, document_embedding)
```
- Uses all-MiniLM-L6-v2 embeddings (384-dimensional vectors)
- Understands semantic meaning beyond keywords
- Neural network-based semantic matching

### 2. Smart Truncation Strategies

**`keep_start`** - Preserves beginning (for instructions, facts, ranked results)
```
[Important content ✅] | [Less critical ❌ TRUNCATED]
```

**`keep_end`** - Preserves end (for chat history, logs, time-series data)
```
[Old context ❌ TRUNCATED] | [Recent content ✅]
```

### 3. Budget Enforcement
```python
def smart_truncate(text, budget, strategy):
    tokens = encoder.encode(text)
    if len(tokens) <= budget:
        return text  # No truncation needed
    
    if strategy == "keep_start":
        return encoder.decode(tokens[:budget])
    else:  # "keep_end"
        return encoder.decode(tokens[-budget:])
```

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Token Reduction** | 60-80% vs unoptimized |
| **Cost Savings** | $360/month per 10k queries |
| **Accuracy** | 90%+ fact verification |
| **Budget Compliance** | 100% (never exceeded) |
| **Response Time** | <100ms context assembly |

## 🧪 Testing & Validation

Run the comprehensive test suite:
```bash
python test_demo.py
```

**6 Integrated Demonstrations:**
1. ✅ Retrieval corpus exploration
2. ✅ Token counting accuracy
3. ✅ Truncation strategy comparison
4. ✅ Budget overflow handling (2-10x scenarios)
5. ✅ Real query assembly with metrics
6. ✅ Cost analysis & summary

## 💼 Business Value

### For Technical Recruiters:
- **System Design** - Clean architecture with separation of concerns
- **Cost Optimization** - Real business value (60-80% savings)
- **AI/ML Knowledge** - Vector embeddings + semantic search with ChromaDB
- **Production Ready** - Comprehensive error handling & testing
- **Full Stack** - Backend logic + CLI + Web UI + Vector DB

### For Engineering Teams:
- **Token Economics** - Understanding LLM cost models
- **Context Management** - Strategic data prioritization
- **Deterministic AI** - Reproducible, auditable behavior
- **Scalable** - Works with any knowledge base
- **Pluggable** - Swap LLM providers (Ollama/OpenAI/Custom)

## 📚 Documentation

- **[ARCHITECTURE_DIAGRAMS.md](docs/ARCHITECTURE_DIAGRAMS.md)** - Visual system design & data flow
- **[IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** - Technical deep dive & algorithms
- **[CONTEXT_OVERFLOW_EXAMPLES.md](docs/CONTEXT_OVERFLOW_EXAMPLES.md)** - Budget overflow scenarios

## 🔧 Configuration

### Budget Customization
Edit `BUDGETS` in `rag_core.py`:
```python
BUDGETS = {
    "instructions": 255,
    "goal": 1500,
    "memory": 55,
    "retrieval": 550,
    "tool_outputs": 855
}
```

### Knowledge Base
ChromaDB is already integrated for vector search! To customize embeddings:
```python
# In assembler.py - Uses ChromaDB with sentence-transformers
def vector_search(query, corpus=None, top_k=3):
    # Automatically embeds query using sentence-transformers
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "distances"]
    )
    return results
```

## 🎓 Key Learnings Demonstrated

1. **Context Economics** - Token budgets enforce cost predictability
2. **Information Retrieval** - Vector embeddings enable semantic understanding
3. **Strategic Truncation** - Different data types need different strategies
4. **Graceful Degradation** - System handles edge cases without crashing
5. **Deterministic AI** - Same input = same output (reproducible)

## 🌟 Use Cases

- **Chatbots** - Manage long conversation histories efficiently
- **Q&A Systems** - Retrieve relevant knowledge without bloat
- **Document Analysis** - Process large corpora within token limits
- **Customer Support** - Prioritize recent interactions
- **Knowledge Management** - Dynamic retrieval with budget constraints

## 📞 Contact & Links

- **Portfolio:** [www.nyiko.co.za](https://www.nyiko.co.za)
- **GitHub:** [github.com/Nyiko-Shabangu](https://github.com/Nyiko-Shabangu)
- **LinkedIn:** [linkedin.com/in/nyikoshabangu](https://www.linkedin.com/in/nyikoshabangu/)

## 📄 License

MIT License - See LICENSE file for details

---

**Built by Nyiko Shabangu** | AI Engineer & Software Developer

*Demonstrating production-grade AI engineering with real business impact*


