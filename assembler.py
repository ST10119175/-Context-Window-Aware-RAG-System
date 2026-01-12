from rag_core import BUDGETS, count_tokens, smart_truncate
import json
import os
import warnings

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    warnings.warn("ChromaDB not installed. Install with: pip install chromadb sentence-transformers")

# --- 1. LOAD KNOWLEDGE BASE FROM JSON (THE "RETRIEVAL" SOURCE) ---

def load_cv_data():
    """Load CV data from cv_data.json and flatten into searchable documents."""
    json_path = os.path.join(os.path.dirname(__file__), 'cv_data.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cv_json = json.load(f)
    except FileNotFoundError:
        print(f"Warning: cv_data.json not found at {json_path}. Using fallback data.")
        return get_fallback_cv_data()
    except json.JSONDecodeError:
        print(f"Warning: cv_data.json is invalid JSON. Using fallback data.")
        return get_fallback_cv_data()
    
    # Extract searchable documents from JSON structure
    documents = []
    
    # Add summary if available
    if 'summary' in cv_json:
        documents.append(cv_json['summary'])
    
    # Add experience highlights
    if 'experience' in cv_json:
        for exp in cv_json['experience']:
            if 'role' in exp and 'company' in exp:
                documents.append(f"{exp.get('role')} at {exp.get('company')}: {' '.join(exp.get('highlights', []))}")
    
    # Add skills
    if 'skills' in cv_json:
        for skill_cat in cv_json['skills']:
            if 'skills' in skill_cat:
                documents.append(f"Skills in {skill_cat.get('category', 'General')}: {', '.join(skill_cat['skills'])}")
    
    # Add education
    if 'education' in cv_json:
        for edu in cv_json['education']:
            documents.append(f"Degree: {edu.get('degree')} from {edu.get('institution')}")
    
    # Add certifications
    if 'certifications' in cv_json:
        for cert in cv_json['certifications']:
            documents.append(f"Certification: {cert.get('name')} ({cert.get('status', 'Completed')})")
    
    # Add personal info
    if 'personal_info' in cv_json:
        personal = cv_json['personal_info']
        documents.append(f"Name: {personal.get('name')}, Role: {personal.get('role')}, Location: {personal.get('location')}")
        if 'links' in personal:
            documents.append(f"Portfolio: {personal['links'].get('portfolio', 'N/A')}")
    
    # Return flattened searchable documents, fallback to summary if empty
    return documents if documents else get_fallback_cv_data()

def get_fallback_cv_data():
    """Fallback CV data if JSON cannot be loaded."""
    return [
        "Nyiko Shabangu is an AI Engineer and Software Developer based in Centurion, South Africa.",
        "He specializes in Python, Vertex AI, Dialogflow, and AWS cloud architecture.",
        "He currently works at GotBot AI (starting June 2025) developing Multi-Agent LLM systems.",
        "He built a 'RAG Anime Discovery Engine' using LangChain and ChromaDB.",
        "He holds a Bachelor of Computer and Information Sciences in Application Development.",
        "He is an AWS Cloud Practitioner and is actively pursuing the Solutions Architect certification.",
        "He previously managed auctions for Kelani Auctions, optimizing revenue by 15%.",
        "He is fluent in English and Xitsonga.",
        "He has experience modding RPG games (Skyrim) using JSON and scripting.",
        "Contact Him at www.nyiko.co.za"
    ]

# Load CV data on module import
CV_DATA = load_cv_data()

# --- 2. INITIALIZE CHROMADB VECTOR DATABASE ---

def initialize_chromadb():
    """Initialize ChromaDB with sentence-transformers embeddings."""
    if not CHROMADB_AVAILABLE:
        print("Warning: ChromaDB not available. Install with: pip install chromadb sentence-transformers")
        return None, {}
    
    try:
        # Create ChromaDB client with persistent storage
        client = chromadb.EphemeralClient()
        
        # Create or get collection with default embedding function
        # ChromaDB uses sentence-transformers by default (all-MiniLM-L6-v2)
        # all-MiniLM-L6-v2: 384-dimensional embeddings, excellent for semantic search
        collection = client.get_or_create_collection(
            name="cv_documents",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for embeddings
        )
        
        # Add documents to the collection
        # ChromaDB will automatically embed them using all-MiniLM-L6-v2
        doc_ids = [f"doc_{i}" for i in range(len(CV_DATA))]
        collection.add(
            ids=doc_ids,
            documents=CV_DATA,
            metadatas=[{"source": "cv_data", "index": i} for i in range(len(CV_DATA))]
        )
        
        print(f"✅ ChromaDB initialized with {len(CV_DATA)} documents using all-MiniLM-L6-v2 embeddings")
        return client, {"collection": collection, "doc_ids": doc_ids}
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        print("Falling back to keyword search.")
        return None, {}

# Initialize ChromaDB on module import
CHROMADB_CLIENT = None
CHROMADB_CONFIG = {}

if CHROMADB_AVAILABLE:
    try:
        CHROMADB_CLIENT, CHROMADB_CONFIG = initialize_chromadb()
    except Exception as e:
        print(f"Warning: ChromaDB initialization failed: {e}")


def vector_search(user_query, corpus=None, top_k=3):
    """
    Retrieve documents using ChromaDB vector similarity search.
    Uses sentence-transformers embeddings (all-MiniLM-L6-v2) for semantic matching.
    
    Args:
        user_query: User's search query
        corpus: Ignored (uses CV_DATA from ChromaDB)
        top_k: Number of top results to return
    
    Returns:
        List of (document, similarity_score) tuples, sorted by relevance
    """
    if not CHROMADB_AVAILABLE or not CHROMADB_CLIENT:
        print("ChromaDB not available. Falling back to keyword search.")
        return keyword_search(user_query, corpus or CV_DATA, top_k)
    
    try:
        collection = CHROMADB_CONFIG.get("collection")
        if not collection:
            return keyword_search(user_query, corpus or CV_DATA, top_k)
        
        # Query the collection - ChromaDB returns distances, we convert to similarity scores
        results = collection.query(
            query_texts=[user_query],
            n_results=top_k,
            include=["documents", "distances", "metadatas"]
        )
        
        # Convert distances to similarity scores (1 - distance for cosine)
        # ChromaDB returns distances in [0, 2] for cosine, so similarity = 1 - distance
        documents = results["documents"][0] if results["documents"] else []
        distances = results["distances"][0] if results["distances"] else []
        
        # Convert distances to similarity scores (higher is better)
        similarity_scores = [1 - dist for dist in distances]
        
        return list(zip(documents, similarity_scores))
    
    except Exception as e:
        print(f"Vector search failed: {e}. Falling back to keyword search.")
        return keyword_search(user_query, corpus or CV_DATA, top_k)


def keyword_search(user_query, corpus, top_k=3):
    """
    Fallback keyword-based search using simple substring matching.
    Used when ChromaDB is not available.
    
    Args:
        user_query: User's search query
        corpus: List of documents to search
        top_k: Number of top results to return
    
    Returns:
        List of (document, relevance_score) tuples
    """
    query_lower = user_query.lower()
    query_terms = query_lower.split()
    
    scores = []
    for doc in corpus:
        doc_lower = doc.lower()
        # Simple scoring: count matching terms
        score = sum(1 for term in query_terms if term in doc_lower)
        scores.append((doc, float(score)))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def semantic_search(user_query, corpus=None, top_k=3):
    """
    Main retrieval function - uses vector search via ChromaDB.
    Falls back to keyword search if ChromaDB is not available.
    
    Args:
        user_query: User's search query
        corpus: Ignored (uses CV_DATA from ChromaDB)
        top_k: Number of top results to return
    
    Returns:
        List of (document, score) tuples, sorted by relevance (highest first)
    """
    if CHROMADB_AVAILABLE and CHROMADB_CLIENT:
        return vector_search(user_query, corpus, top_k)
    else:
        return keyword_search(user_query, corpus or CV_DATA, top_k)


def build_context_window(user_query, chat_history):
    """
    The 'Brain' of the operation. 
    It assembles the final prompt by enforcing strict token budgets 
    per section using the rules defined in rag_core.
    """
    sections = {}

    # --- STEP 1: INSTRUCTIONS (Budget: 255) ---
    # Strategy: 'keep_start' 
    # Why: The core persona definition is usually at the very beginning.
    sys_prompt = (
        "You are an AI assistant representing Nyiko Shabangu. "
        "Answer questions accurately based ONLY on the provided Context. "
        "If the answer is not in the context, say you don't know. "
        "Be professional, concise, and highlight his engineering skills."
    )
    sections['instructions'] = smart_truncate(sys_prompt, BUDGETS['instructions'], "keep_start")

    # --- STEP 2: RETRIEVAL (Budget: 550) ---
    # Strategy: Vector Semantic Search (ChromaDB) -> Then 'keep_start' if it overflows
    # Why: We use sentence-transformers embeddings (all-MiniLM-L6-v2) for semantic matching.
    #      This finds documents based on meaning, not just keywords.
    #      If too many results, we keep the highest-scoring (most relevant) ones.
    
    # Perform semantic vector search using ChromaDB
    search_results = semantic_search(user_query, CV_DATA, top_k=5)
    
    # Extract just the documents (with scores for debugging)
    if search_results:
        hits = [doc for doc, score in search_results]
    else:
        # Fallback: Show general summary (first 3 lines)
        hits = CV_DATA[:3]
        search_results = [(doc, 0.0) for doc in hits]
    
    # Build retrieval section with metadata
    retrieval_method = "Vector Search (ChromaDB/all-MiniLM-L6-v2)" if CHROMADB_AVAILABLE else "Keyword Search"
    raw_retrieval = f"RELEVANT CV DATA ({retrieval_method}):\n" + "\n".join(
        f"- {doc} (similarity: {score:.2f})" 
        if score > 0 else f"- {doc}"
        for doc, score in search_results
    )
    
    sections['retrieval'] = smart_truncate(raw_retrieval, BUDGETS['retrieval'], "keep_start")

    # --- STEP 3: TOOLS / SYSTEM LOGS (Budget: 855) ---
    # Strategy: 'keep_end'
    # Why: We only care about the most recent tool execution (e.g., the last API call status).
    # Mocking a tool log for demonstration:
    mock_tools = f"[System Log] Processing query: '{user_query}'... Retrieval complete. 3 documents found."
    sections['tool_outputs'] = smart_truncate(mock_tools, BUDGETS['tool_outputs'], "keep_end")

    # --- STEP 4: MEMORY (Budget: 55) ---
    # Strategy: 'keep_start'
    # Why: This is for high-density, static facts that must never be forgotten.
    static_memory = "Role: Job Candidate Bot. Location: ZA. Status: Hired."
    sections['memory'] = smart_truncate(static_memory, BUDGETS['memory'], "keep_start")

    # --- STEP 5: GOAL / CONVERSATION HISTORY (Budget: 1500) ---
    # Strategy: 'keep_end' (Sliding Window)
    # Why: In a chat, the most recent message is the most important. We drop old turns.
    full_conversation = chat_history + f"\nUser: {user_query}"
    sections['goal'] = smart_truncate(full_conversation, BUDGETS['goal'], "keep_end")

    # --- STEP 6: FINAL ASSEMBLY ---
    # We construct the final string that goes to the LLM.
    # Note how we label sections clearly for the model.
    final_prompt = f"""
    ### SYSTEM INSTRUCTIONS
    {sections['instructions']}

    ### LONG TERM MEMORY
    {sections['memory']}

    ### CONTEXT (RETRIEVED KNOWLEDGE)
    {sections['retrieval']}

    ### SYSTEM TOOLS
    {sections['tool_outputs']}

    ### CONVERSATION HISTORY
    {sections['goal']}
    
    ### ASSISTANT RESPONSE:
    """
    
    # Return both the prompt (for the LLM) and the sections (for the Dashboard UI)
    return final_prompt, sections