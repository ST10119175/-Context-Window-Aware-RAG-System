# ⚡ Quick Start Guide

**Get the system running in under 5 minutes**

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/ST10119175/-Context-Window-Aware-RAG-System.git
cd -Context-Window-Aware-RAG-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web UI framework
- `tiktoken` - Token counting (OpenAI standard)
- `requests` - HTTP client
- `python-dotenv` - Environment configuration

### 3. Verify Installation
```bash
python verify_setup.py
```

Expected output:
```
✅ Python 3.8+ detected
✅ All required packages installed
✅ Core files present
✅ System ready to use
```

## Running the System

### Option 1: Interactive CLI (Recommended for First Time)
```bash
python cli.py
```

**Try these queries:**
- "Who is Nyiko Shabangu?"
- "Tell me about your AI experience"
- "What are your cloud certifications?"

### Option 2: Web Dashboard
```bash
streamlit run app.py
```

Opens in browser at `http://localhost:8501`

Features:
- Real-time token visualization
- Interactive chat interface
- Budget breakdown dashboard
- Multiple LLM provider support

### Option 3: Test Suite (See All Features)
```bash
python test_demo.py
```

Runs 6 comprehensive demonstrations:
1. Corpus exploration
2. Token counting validation
3. Truncation strategies
4. Budget overflow handling
5. Real query assembly
6. Cost analysis

## Understanding the Output

### CLI Output Example:
```
USER QUERY: Tell me about your AI experience.

[BM25 Search]
  [1] Score: 0.921 - AI Engineer and Software Developer...
  [2] Score: 0.809 - GotBot AI Multi-Agent systems...

[Context Assembly]
  INSTRUCTIONS      48/ 255 tokens  ✅
  RETRIEVAL        243/ 550 tokens  ✅
  MEMORY            16/  55 tokens  ✅
  GOAL              10/1500 tokens  ✅
  TOOL_OUTPUTS      24/ 855 tokens  ✅
  ────────────────────────────────────
  TOTAL            341/3215 tokens  (10.6%)
```

### What This Shows:
- ✅ **Budget Enforcement** - Each section within limits
- ✅ **Token Efficiency** - Only 10.6% of budget used
- ✅ **BM25 Ranking** - Relevance scores for retrieved docs
- ✅ **Cost Savings** - 96.6% less than unoptimized approach

## Customization

### Change Knowledge Base
Edit `cv_data.json` with your own data:
```json
{
  "personal_info": {
    "name": "Your Name",
    "role": "Your Role"
  },
  "experience": [
    {
      "role": "Position",
      "company": "Company Name",
      "highlights": ["Achievement 1", "Achievement 2"]
    }
  ]
}
```

### Adjust Token Budgets
Edit `rag_core.py`:
```python
BUDGETS = {
    "instructions": 255,   # System prompt
    "goal": 1500,          # Chat history
    "memory": 55,          # Static facts
    "retrieval": 550,      # Search results
    "tool_outputs": 855    # System logs
}
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'tiktoken'`
**Solution:** Run `pip install -r requirements.txt`

### Issue: Streamlit command not found
**Solution:** Run `python -m streamlit run app.py`

### Issue: Port 8501 already in use
**Solution:** Kill existing process or use different port:
```bash
streamlit run app.py --server.port 8502
```

## Next Steps

1. ✅ **Read the README** - System overview and architecture
2. ✅ **Try CLI queries** - Interactive experience
3. ✅ **Run test suite** - See all features
4. ✅ **Explore docs/** - Technical deep dive
5. ✅ **Check examples/** - Advanced demonstrations

## For Recruiters

**To evaluate this project quickly:**

1. Run `python verify_setup.py` - Confirms working environment
2. Run `python test_demo.py` - See 6 demos in 2 minutes
3. Review `README.md` - System capabilities
4. Check `docs/ARCHITECTURE_DIAGRAMS.md` - Visual design

**Key evaluation points:**
- ✅ Production-ready code (1,000+ lines)
- ✅ Comprehensive testing (6 demos)
- ✅ Clean architecture
- ✅ Professional documentation
- ✅ Real business value (60-80% cost reduction)

## Questions?

- **Portfolio:** www.nyiko.co.za
- **GitHub:** github.com/Nyiko-Shabangu
- **LinkedIn:** linkedin.com/in/nyikoshabangu

---

**Total setup time: ~5 minutes** ⚡
