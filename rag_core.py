import tiktoken

# --- 1. CONFIGURATION: HARD TOKEN BUDGETS ---

# The assembler must never exceed these limits per section.
BUDGETS = {
    "instructions": 255,   # System Prompt
    "goal": 1500,          # Conversation History (The moving window)
    "memory": 55,          # Long-term static facts
    "retrieval": 550,      # Dynamic knowledge (CV Data)
    "tool_outputs": 855    # Logs from function calls
}

# --- 2. TOKEN ENCODER SETUP ---
# We use 'cl100k_base' (GPT-4 standard). 
# While Llama 3 has a slightly different tokenizer, this provides a 
# safe, industry-standard approximation for budget management.
encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """
    Returns the exact number of tokens in a text string.
    Used to audit the context window before sending to the LLM.
    """
    if not text:
        return 0
    return len(encoder.encode(text))

def smart_truncate(text: str, budget: int, strategy: str = "keep_start") -> str:
    """
    Truncates text to fit a specific budget based on data importance.
    
    Args:
        text: The string to process.
        budget: Max allowed tokens.
        strategy: 
            - 'keep_start': Truncates the end. (Best for Instructions/Facts)
            - 'keep_end': Truncates the start. (Best for Chat History/Logs)
    """
    tokens = encoder.encode(text)
    
    # If it fits within budget, return as-is
    if len(tokens) <= budget:
        return text
    
    # Apply Truncation Logic
    if strategy == "keep_start":
        # Keep the BEGINNING (e.g., "You are a helpful assistant...")
        truncated_tokens = tokens[:budget]
    elif strategy == "keep_end":
        # Keep the END (e.g., The most recent user message)
        truncated_tokens = tokens[-budget:]
    else:
        # Default fallback
        truncated_tokens = tokens[:budget]
        
    return encoder.decode(truncated_tokens)