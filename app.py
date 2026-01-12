import streamlit as st
import requests
import json
import os
from assembler import build_context_window, CV_DATA
from rag_core import BUDGETS, count_tokens
from dotenv import load_dotenv

# --- CONFIGURATION ---
# If you are hosting Ollama on the same server, use "http://localhost:11434/api/generate"
# If hosting on a separate VM (Oracle/AWS), put that IP here.
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Ensure you have pulled this model: `ollama pull llama3`

# Optional: load overrides from .env (e.g., OLLAMA_URL, MODEL_NAME)
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", OLLAMA_URL)
MODEL_NAME = os.getenv("MODEL_NAME", MODEL_NAME)

# Optional: Alternative hosted chat API (Vercel) overrides
VERCEL_CHAT_URL = os.getenv(
    "VERCEL_CHAT_URL",
)
VERCEL_API_KEY = os.getenv("VERCEL_API_KEY")

st.set_page_config(layout="wide", page_title="Nyiko's Context-Aware RAG")

# --- HEADER ---
st.title("🧠 Context-Window-Aware RAG System")
st.markdown("""
**Assessment Goal:** Demonstrate strict adherence to token budgets ('Context Economics') 
before sending data to the LLM.
* **Architecture:** Python Assembler (Logic) + Ollama (Inference)
* **Budgets:** Instructions (255), Goal (1500), Retrieval (550), Tools (855), Memory (55)
""")
st.divider()

# Provider selection
with st.sidebar:
    st.subheader("Inference Provider")
    provider = st.selectbox(
        "Choose backend",
        options=["Ollama", "Vercel API", "Mock"],
        index=0,
    )
    if provider == "Ollama":
        st.caption(f"URL: {OLLAMA_URL}")
        st.caption(f"Model: {MODEL_NAME}")
    elif provider == "Vercel API":
        st.caption(f"URL: {VERCEL_CHAT_URL}")
        st.caption("Header: X-API-Key (from env)")

# --- SESSION STATE (Chat History) ---
if "history" not in st.session_state:
    st.session_state.history = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LAYOUT: 2 COLUMNS ---
# Left: The Chat Interface
# Right: The Engineering Dashboard (The "Proof" for Deloitte)
col_chat, col_debug = st.columns([3, 2])

with col_chat:
    st.subheader("💬 Interview Simulator")
    
    # Display Chat Log
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_input = st.chat_input("Ask about Nyiko's experience...")

    if user_input:
        # 1. DISPLAY USER MESSAGE
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. INVOKE THE ASSEMBLER (The Core Logic)
        # We pass the full history string to the assembler to handle the "sliding window"
        final_prompt, usage_report = build_context_window(user_input, st.session_state.history)

        # 3. CALL INFERENCE PROVIDER (Ollama or Vercel API)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                if provider == "Ollama":
                    # Prepare payload for Ollama
                    payload = {
                        "model": MODEL_NAME,
                        "prompt": final_prompt,
                        "stream": False,
                    }
                    with st.spinner("Thinking with Ollama (and budgeting tokens)..."):
                        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
                    if response.status_code == 200:
                        data = response.json()
                        ai_reply = data.get("response", "")
                    else:
                        # Try to parse error details
                        error_detail = ""
                        try:
                            err_json = response.json()
                            error_detail = err_json.get("error", "")
                        except Exception:
                            pass
                        guidance = ""
                        if response.status_code == 404:
                            guidance = (
                                f"\n\n➡️ Tip: If the model '{MODEL_NAME}' is not pulled, run: "
                                f"`ollama pull {MODEL_NAME}` in PowerShell, then retry."
                            )
                        server_hint = (
                            f"\n\n➡️ Verify server: `Invoke-RestMethod -Uri {OLLAMA_URL.replace('/api/generate','/api/version')}`"
                        )
                        ai_reply = (
                            f"⚠️ **Ollama Error:** Status {response.status_code}. {error_detail}{guidance}{server_hint}\n\n"
                            "**[MOCK RESPONSE]** Nyiko is an AI Engineer specializing in RAG systems..."
                        )
                elif provider == "Vercel API":
                    headers = {
                        "X-API-Key": VERCEL_API_KEY,
                        "Content-Type": "application/json",
                    }
                    body = {"message": final_prompt}
                    with st.spinner("Thinking via Vercel API (and budgeting tokens)..."):
                        response = requests.post(
                            VERCEL_CHAT_URL, headers=headers, json=body, timeout=60
                        )
                    if response.status_code == 200:
                        # Try to parse common JSON shapes, else fallback to text
                        ai_reply = ""
                        try:
                            data = response.json()
                            # Check for 'response' first (from curl output), then 'message', then others
                            for key in ("response", "message", "reply", "output"):
                                if key in data and isinstance(data[key], str):
                                    ai_reply = data[key]
                                    break
                            if not ai_reply:
                                ai_reply = json.dumps(data, ensure_ascii=False)
                        except Exception as e:
                            ai_reply = f"Parse error: {str(e)}\n\nRaw: {response.text}"
                    else:
                        ai_reply = (
                            f"⚠️ **Vercel API Error:** Status {response.status_code}. "
                            f"Body: {response.text[:300]}\n\n"
                            "**[MOCK RESPONSE]** Nyiko is an AI Engineer specializing in RAG systems..."
                        )
                else:
                    # Explicit mock mode
                    ai_reply = (
                        "**[MOCK RESPONSE]**\n\n"
                        "Running in mock mode. Context Assembly executed successfully. "
                        "Check the dashboard for token economics.\n\n"
                        "Nyiko is an AI Engineer specializing in RAG systems..."
                    )
            
            except requests.exceptions.ConnectionError:
                # FALLBACK: If Ollama isn't running, we still show the Budget Logic worked!
                ai_reply = (
                    "**[MOCK RESPONSE]**\n\n"
                    "*(Ollama server not detected. However, the Context Assembly Logic executed successfully. "
                    "Check the dashboard on the right to see the token economics at work!)*\n\n"
                    "Nyiko is an AI Engineer specializing in RAG systems..."
                )
            
            # Render response
            message_placeholder.markdown(ai_reply)
            
            # Update Session State
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state.history += f"\nUser: {user_input}\nAI: {ai_reply}"

# --- RIGHT COLUMN: THE DASHBOARD ---
with col_debug:
    st.subheader("⚙️ Context Economics Debugger")
    st.info("This panel visualizes the 'Budget Enforcement' logic required by the assessment.")

    # Only show metrics if a query has been run
    if user_input:
        st.caption(f"Provider: {provider}")
        st.markdown("### Token Usage per Section")
        
        total_used = 0
        total_budget = 0
        truncation_count = 0
        
        for section_name, content in usage_report.items():
            used = count_tokens(content)
            limit = BUDGETS.get(section_name, 1000)
            total_used += used
            total_budget += limit
            
            # Calculate percentage for progress bar
            pct = min(used / limit, 1.0)
            is_truncated = used >= limit
            if is_truncated:
                truncation_count += 1
            
            # Determine color based on usage
            bar_color = "green"
            status_text = "✅ OK"
            if is_truncated:
                bar_color = "red"
                status_text = "⚠️ TRUNCATED"
            
            # Render the metric
            col_metric, col_bar = st.columns([1, 2])
            with col_metric:
                st.write(f"**{section_name.upper()}**")
                st.caption(f"{used} / {limit} tokens")
            with col_bar:
                st.progress(pct)
                st.caption(status_text)
            
            st.markdown("---")
        
        # Summary
        pct_total = (total_used / total_budget) * 100
        st.markdown(f"**Total Context Size:** {total_used} / {total_budget} tokens ({pct_total:.1f}%)")
        if truncation_count > 0:
            st.warning(f"⚠️ **{truncation_count} section(s) truncated** to fit budget constraints")
        else:
            st.success("✅ **All sections fit within budgets** - No truncation needed")

        # Show the actual assembled text to prove it exists
        with st.expander("📄 Inspect Final Assembled Context"):
            st.text("This is the exact string sent to the LLM:")
            st.code(final_prompt, language="markdown")
            
        # Show retrieval details
        with st.expander("🔍 Retrieval Details"):
            from assembler import semantic_search
            search_results = semantic_search(user_input, CV_DATA, top_k=5)
            st.markdown("**Top Retrieved Documents (by BM25 relevance):**")
            for idx, (doc, score) in enumerate(search_results, 1):
                st.caption(f"[{idx}] Score: {score:.3f} → {doc}")
    else:
        st.markdown("*Waiting for first query...*")