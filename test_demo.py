#!/usr/bin/env python3
"""
Test & Demo Script for Context-Window-Aware RAG System

This script demonstrates:
1. The complete context assembly pipeline
2. Budget enforcement for all 5 sections
3. Truncation strategies when budgets are exceeded
4. Real token counting using tiktoken
"""

from assembler import build_context_window, CV_DATA
from rag_core import BUDGETS, count_tokens, smart_truncate
import textwrap

# ============================================================================
# UTILITY: Pretty Print with Color
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title, content=""):
    """Print a formatted section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    if content:
        print(content)


def print_metric(name, used, budget, truncated=False):
    """Print token usage metric with color coding."""
    pct = (used / budget) * 100
    status = "✅ OK" if used <= budget else f"⚠️  TRUNCATED ({pct:.0f}%)"
    color = Colors.OKGREEN if used <= budget else Colors.FAIL
    
    print(f"{color}{name:20} {used:4} / {budget:4} tokens {status}{Colors.ENDC}")


# ============================================================================
# DEMO 1: Show the Mock Data (CV_DATA)
# ============================================================================
def demo_retrieval_corpus():
    print_section("DEMO 1: Retrieval Corpus (Mock Knowledge Base)")
    print(f"Total documents in CV_DATA: {len(CV_DATA)}\n")
    
    for idx, line in enumerate(CV_DATA, 1):
        tokens = count_tokens(line)
        print(f"  [{idx}] ({tokens} tokens) {line[:60]}...")


# ============================================================================
# DEMO 2: Token Counting Accuracy
# ============================================================================
def demo_token_counting():
    print_section("DEMO 2: Token Counting (tiktoken cl100k_base)")
    
    test_cases = [
        ("Hello world", "Simple phrase"),
        ("You are an AI assistant representing Nyiko Shabangu.", "System prompt"),
        (CV_DATA[0], "First CV line"),
        ("\n".join(CV_DATA[:3]), "First 3 CV lines"),
    ]
    
    for text, label in test_cases:
        tokens = count_tokens(text)
        preview = text[:50] + "..." if len(text) > 50 else text
        print(f"{Colors.OKCYAN}{label:25} → {tokens:4} tokens{Colors.ENDC}")
        print(f"  Preview: {preview}\n")


# ============================================================================
# DEMO 3: Truncation Strategies
# ============================================================================
def demo_truncation_strategies():
    print_section("DEMO 3: Truncation Strategies in Action")
    
    # Create a long text (200 tokens) and truncate to 50
    long_text = "This is a sentence. " * 30  # Repeat to create ~600 tokens
    
    print(f"\n{Colors.BOLD}Original text:{Colors.ENDC}")
    print(f"  Length: {len(long_text)} chars, {count_tokens(long_text)} tokens")
    print(f"  Preview: {long_text[:100]}...\n")
    
    # Test KEEP_START
    truncated_start = smart_truncate(long_text, 50, "keep_start")
    print(f"{Colors.OKBLUE}Strategy: KEEP_START (keep beginning){Colors.ENDC}")
    print(f"  Result: {count_tokens(truncated_start)} tokens (budget=50)")
    print(f"  Text: {truncated_start[:80]}...\n")
    
    # Test KEEP_END
    truncated_end = smart_truncate(long_text, 50, "keep_end")
    print(f"{Colors.OKBLUE}Strategy: KEEP_END (keep end){Colors.ENDC}")
    print(f"  Result: {count_tokens(truncated_end)} tokens (budget=50)")
    print(f"  Text: ...{truncated_end[-80:]}\n")


# ============================================================================
# DEMO 4: Budget Overflow Scenarios
# ============================================================================
def demo_budget_overflow():
    """Test each section with oversized data to show truncation in action."""
    print_section("DEMO 4: Budget Overflow Handling (Each Section)")
    
    # === Scenario 1: Instructions overflow ===
    print(f"\n{Colors.BOLD}1. INSTRUCTIONS (Budget: 255 tokens){Colors.ENDC}")
    long_instructions = (
        "You are a world-class AI assistant representing Nyiko Shabangu. "
        "You must answer questions with extreme accuracy and clarity. "
        "You should provide detailed explanations, cite sources, and always be professional. "
        "You should highlight engineering achievements and cloud expertise. "
        "You should mention specific technologies, frameworks, and methodologies. "
        "If information is not available, admit that clearly. " * 5
    )
    
    original_tokens = count_tokens(long_instructions)
    truncated_instructions = smart_truncate(long_instructions, BUDGETS['instructions'], "keep_start")
    truncated_tokens = count_tokens(truncated_instructions)
    
    print(f"  Original: {original_tokens} tokens")
    print(f"  Truncated: {truncated_tokens} tokens (budget: {BUDGETS['instructions']})")
    print(f"  Strategy: keep_start (preserve the core persona definition)")
    print(f"  ✓ Result text: {truncated_instructions[:80]}...")
    
    # === Scenario 2: Retrieval overflow ===
    print(f"\n{Colors.BOLD}2. RETRIEVAL (Budget: 550 tokens){Colors.ENDC}")
    # Duplicate all CV_DATA multiple times to create overflow
    expanded_retrieval = "RELEVANT CV DATA:\n- " + "\n- ".join(CV_DATA * 8)
    
    original_tokens = count_tokens(expanded_retrieval)
    truncated_retrieval = smart_truncate(expanded_retrieval, BUDGETS['retrieval'], "keep_start")
    truncated_tokens = count_tokens(truncated_retrieval)
    
    print(f"  Original: {original_tokens} tokens")
    print(f"  Truncated: {truncated_tokens} tokens (budget: {BUDGETS['retrieval']})")
    print(f"  Strategy: keep_start (preserve most relevant matches)")
    print(f"  ✓ Result lines: {truncated_retrieval.count(chr(10))} lines kept")
    
    # === Scenario 3: Goal (Chat History) overflow ===
    print(f"\n{Colors.BOLD}3. GOAL / CONVERSATION (Budget: 1500 tokens){Colors.ENDC}")
    # Create a long chat history
    long_history = ""
    for i in range(20):
        long_history += f"User: Tell me about your experience with {'AWS' if i % 2 == 0 else 'Python'}.\n"
        long_history += f"AI: Nyiko has deep expertise in this area with multiple projects. " * 10
        long_history += "\n"
    
    original_tokens = count_tokens(long_history)
    truncated_goal = smart_truncate(long_history, BUDGETS['goal'], "keep_end")
    truncated_tokens = count_tokens(truncated_goal)
    
    print(f"  Original: {original_tokens} tokens")
    print(f"  Truncated: {truncated_tokens} tokens (budget: {BUDGETS['goal']})")
    print(f"  Strategy: keep_end (preserve most recent messages - sliding window)")
    print(f"  ✓ Result lines: {truncated_goal.count('User:')}-{truncated_goal.count('AI:')} exchanges kept")
    
    # === Scenario 4: Tool Outputs overflow ===
    print(f"\n{Colors.BOLD}4. TOOL OUTPUTS (Budget: 855 tokens){Colors.ENDC}")
    large_logs = "[System Log] " * 200 + "Processing query... Retrieval complete. Multiple documents found and ranked by relevance."
    
    original_tokens = count_tokens(large_logs)
    truncated_tools = smart_truncate(large_logs, BUDGETS['tool_outputs'], "keep_end")
    truncated_tokens = count_tokens(truncated_tools)
    
    print(f"  Original: {original_tokens} tokens")
    print(f"  Truncated: {truncated_tokens} tokens (budget: {BUDGETS['tool_outputs']})")
    print(f"  Strategy: keep_end (preserve most recent log entries)")
    print(f"  ✓ Result: {truncated_tools[-70:]}...")
    
    # === Scenario 5: Memory (tight budget) ===
    print(f"\n{Colors.BOLD}5. MEMORY (Budget: 55 tokens - Very Tight){Colors.ENDC}")
    large_memory = "Role: Job Candidate Bot. Status: Hired. Location: Centurion, South Africa. " * 5
    
    original_tokens = count_tokens(large_memory)
    truncated_memory = smart_truncate(large_memory, BUDGETS['memory'], "keep_start")
    truncated_tokens = count_tokens(truncated_memory)
    
    print(f"  Original: {original_tokens} tokens")
    print(f"  Truncated: {truncated_tokens} tokens (budget: {BUDGETS['memory']})")
    print(f"  Strategy: keep_start (preserve high-density critical facts)")
    print(f"  ✓ Result: {truncated_memory}")


# ============================================================================
# DEMO 5: Real Query Assembly
# ============================================================================
def demo_real_query_assembly():
    print_section("DEMO 5: Complete Query Assembly Pipeline")
    
    test_queries = [
        "Tell me about your AI experience.",
        "What are your cloud certifications?",
        "Describe your work with LLMs and RAG systems.",
    ]
    
    chat_history = ""
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n{Colors.BOLD}Query #{idx}: {Colors.OKCYAN}{query}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'-'*80}{Colors.ENDC}")
        
        # Build context window
        final_prompt, usage_report = build_context_window(query, chat_history)
        
        # Display metrics
        total_tokens = 0
        for section_name, content in usage_report.items():
            used = count_tokens(content)
            budget = BUDGETS[section_name]
            truncated = used >= budget
            total_tokens += used
            print_metric(section_name.upper(), used, budget, truncated)
        
        print(f"{Colors.BOLD}{'-'*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Total context size: {total_tokens} tokens{Colors.ENDC}")
        
        # Update history for next iteration (simulate conversation)
        chat_history += f"\nUser: {query}\nAI: [Response would go here]"


# ============================================================================
# DEMO 6: Summary Dashboard
# ============================================================================
def demo_summary_dashboard():
    print_section("DEMO 6: Budget Summary & Configuration")
    
    print(f"\n{Colors.BOLD}Current Budget Configuration:{Colors.ENDC}")
    total_budget = sum(BUDGETS.values())
    
    for section, budget in BUDGETS.items():
        percentage = (budget / total_budget) * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {section:15} {budget:5} tokens ({percentage:5.1f}%) {bar}")
    
    print(f"\n{Colors.BOLD}Total Context Budget: {total_budget} tokens{Colors.ENDC}")
    print(f"  (Safe for context windows up to ~4k-8k tokens with overhead)")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  CONTEXT-WINDOW-AWARE RAG SYSTEM - COMPREHENSIVE TEST SUITE  ".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    print(f"{Colors.ENDC}\n")
    
    # Run all demos
    demo_retrieval_corpus()
    demo_token_counting()
    demo_truncation_strategies()
    demo_budget_overflow()
    demo_real_query_assembly()
    demo_summary_dashboard()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ All demos completed successfully!{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
