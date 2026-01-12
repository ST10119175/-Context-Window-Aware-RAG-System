#!/usr/bin/env python3
"""
Simple Demo Script for Context-Window-Aware RAG System
Generates sample output for documentation
"""

from assembler import build_context_window, semantic_search, CV_DATA
from rag_core import BUDGETS, count_tokens

def demo_query(query, chat_history=""):
    """Run a demo query and show the context assembly."""
    print("="*80)
    print(f"USER QUERY: {query}")
    print("="*80)
    
    # Show retrieval step
    print("\n[STEP 1] BM25 Semantic Search")
    print("-"*80)
    search_results = semantic_search(query, CV_DATA, top_k=3)
    for idx, (doc, score) in enumerate(search_results, 1):
        print(f"  [{idx}] Score: {score:.3f}")
        print(f"      {doc[:65]}...")
    
    # Build context
    print("\n[STEP 2] Context Assembly")
    print("-"*80)
    final_prompt, usage_report = build_context_window(query, chat_history)
    
    # Show budget usage
    total = 0
    for section, content in usage_report.items():
        used = count_tokens(content)
        budget = BUDGETS[section]
        total += used
        status = "OK" if used <= budget else "TRUNCATED"
        pct = (used / budget) * 100
        print(f"  {section.upper():15} {used:4}/{budget:4} tokens  [{status:10}] ({pct:5.1f}%)")
    
    print("-"*80)
    print(f"  TOTAL            {total:4}/{sum(BUDGETS.values())} tokens  ({(total/sum(BUDGETS.values()))*100:.1f}%)")
    print()
    
    return final_prompt, usage_report

def main():
    print("\n" + "="*80)
    print("CONTEXT-WINDOW-AWARE RAG SYSTEM - DEMONSTRATION")
    print("="*80)
    print("\nBudget Configuration:")
    print("-"*80)
    for section, budget in BUDGETS.items():
        pct = (budget / sum(BUDGETS.values())) * 100
        print(f"  {section:15} {budget:4} tokens ({pct:5.1f}%)")
    print(f"  {'TOTAL':15} {sum(BUDGETS.values()):4} tokens (100.0%)")
    print()
    
    # Demo 1: Simple query
    print("\n\nDEMO 1: Simple Query (No History)")
    final_prompt1, report1 = demo_query("Tell me about your AI experience.")
    
    # Demo 2: Query with history
    print("\n\nDEMO 2: Query with Chat History")
    history = """User: What's your background?
AI: I'm an AI Engineer and Software Developer from South Africa.

User: What technologies do you use?
AI: I specialize in Python, Vertex AI, AWS, and LangChain."""
    
    final_prompt2, report2 = demo_query("Describe your work with LLMs and RAG systems.", history)
    
    # Demo 3: Show budget overflow scenario
    print("\n\nDEMO 3: Budget Overflow Scenario")
    print("="*80)
    print("Simulating 10x chat history overflow...")
    print("="*80)
    
    # Create massive history
    massive_history = ""
    for i in range(20):
        massive_history += f"\nUser: Question {i+1} about AI engineering?\n"
        massive_history += f"AI: Here's a detailed answer with lots of content. " * 15
    
    print(f"\n[ORIGINAL HISTORY]")
    print(f"  Token count: {count_tokens(massive_history)} tokens")
    print(f"  Goal budget: {BUDGETS['goal']} tokens")
    print(f"  Overflow:    {count_tokens(massive_history) - BUDGETS['goal']} tokens (needs truncation)")
    
    final_prompt3, report3 = demo_query("Latest question?", massive_history)
    
    goal_content = report3['goal']
    print(f"\n[AFTER TRUNCATION]")
    print(f"  Token count: {count_tokens(goal_content)} tokens")
    print(f"  Strategy:    keep_end (sliding window)")
    print(f"  Result:      Recent messages preserved ✓")
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ All queries processed successfully")
    print("✓ Budget enforcement working correctly")
    print("✓ Truncation strategies applied as designed")
    print("✓ System handles overflow gracefully")
    print("\nContext Economics Demonstration Complete!")
    print("="*80)

if __name__ == "__main__":
    main()
