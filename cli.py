#!/usr/bin/env python3
"""
Context-Window-Aware RAG System - CLI Interface

A minimal terminal-based interface for the RAG system that demonstrates:
- Context assembly with strict token budgets
- Budget enforcement and truncation strategies
- Real-time token counting
- Chat-like interaction without needing Streamlit or Ollama

Run: python cli.py
"""

import sys
from assembler import build_context_window, CV_DATA, semantic_search
from rag_core import BUDGETS, count_tokens

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print the application header."""
    header = f"""
{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}║                                                            ║{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}║     🧠 Context-Window-Aware RAG System (CLI)               ║{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}║     Demonstrating Strict Token Budget Enforcement         ║{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}║                                                            ║{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(header)


def print_budget_config():
    """Display the budget configuration."""
    print(f"\n{Colors.BOLD}📊 Budget Configuration:{Colors.ENDC}")
    total = sum(BUDGETS.values())
    
    for section, budget in BUDGETS.items():
        pct = (budget / total) * 100
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  {section:15} {budget:5} tokens ({pct:5.1f}%) {bar}")
    
    print(f"\n  {Colors.OKGREEN}Total: {total} tokens{Colors.ENDC}\n")


def print_usage_report(usage_report):
    """Print the token usage report for each section."""
    print(f"\n{Colors.BOLD}📈 Token Usage per Section:{Colors.ENDC}\n")
    
    total_used = 0
    total_budget = 0
    
    for section_name, content in usage_report.items():
        used = count_tokens(content)
        budget = BUDGETS[section_name]
        total_used += used
        total_budget += budget
        
        pct = min((used / budget) * 100, 100)
        status = "✅" if used <= budget else "⚠️ TRUNCATED"
        color = Colors.OKGREEN if used <= budget else Colors.FAIL
        
        bar_filled = int(pct / 2)
        bar = "█" * bar_filled + "░" * (50 - bar_filled)
        
        print(f"  {Colors.BOLD}{section_name.upper():15}{Colors.ENDC}")
        print(f"    {color}{used:4} / {budget:4}{Colors.ENDC} tokens  {status}  {pct:5.1f}%")
        print(f"    {bar}")
        print()
    
    pct_total = (total_used / total_budget) * 100
    print(f"  {Colors.BOLD}TOTAL: {total_used} / {total_budget} tokens ({pct_total:.1f}%){Colors.ENDC}")


def print_retrieval_section(user_query):
    """Show what was retrieved for the query."""
    print(f"\n{Colors.BOLD}🔍 Retrieval Results for: \"{user_query}\"{Colors.ENDC}\n")
    
    search_results = semantic_search(user_query, CV_DATA, top_k=5)
    
    if search_results:
        for idx, (doc, score) in enumerate(search_results, 1):
            tokens = count_tokens(doc)
            print(f"  [{idx}] Score: {score:.3f} ({tokens} tokens)")
            print(f"      {doc[:70]}{'...' if len(doc) > 70 else ''}\n")
    else:
        print(f"  {Colors.OKYELLOW}No results found (using fallback){Colors.ENDC}\n")


def print_assembled_context(final_prompt):
    """Display the assembled context for inspection."""
    print(f"\n{Colors.BOLD}📄 Final Assembled Context:{Colors.ENDC}\n")
    print(f"Total size: {Colors.OKGREEN}{count_tokens(final_prompt)} tokens{Colors.ENDC}\n")
    print("-" * 70)
    print(final_prompt)
    print("-" * 70)


def interactive_chat():
    """Run an interactive chat session."""
    print_header()
    print(f"\n{Colors.OKCYAN}Welcome to the Context-Window-Aware RAG System!{Colors.ENDC}")
    print(f"\nThis system demonstrates strict token budget enforcement.")
    print(f"Each section has a hard limit, and content is truncated intelligently.")
    print(f"\nAvailable commands:")
    print(f"  • Type a question about Nyiko to get started")
    print(f"  • Type 'budget' to see the configuration")
    print(f"  • Type 'demo' to see all retrieval docs")
    print(f"  • Type 'quit' to exit\n")
    
    chat_history = ""
    query_count = 0
    
    while True:
        try:
            user_input = input(f"{Colors.OKBLUE}You:{Colors.ENDC} ").strip()
        except EOFError:
            print(f"\n{Colors.OKYELLOW}Exiting...{Colors.ENDC}")
            break
        except KeyboardInterrupt:
            print(f"\n{Colors.OKYELLOW}Interrupted. Exiting...{Colors.ENDC}")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print(f"{Colors.OKYELLOW}Goodbye!{Colors.ENDC}")
            break
        
        if user_input.lower() == "budget":
            print_budget_config()
            continue
        
        if user_input.lower() == "demo":
            print(f"\n{Colors.BOLD}📚 All Documents in CV_DATA:{Colors.ENDC}\n")
            for idx, doc in enumerate(CV_DATA, 1):
                tokens = count_tokens(doc)
                print(f"  [{idx:2}] ({tokens:3} tokens) {doc}")
            print()
            continue
        
        # Process as a query
        query_count += 1
        print(f"\n{Colors.BOLD}Processing query #{query_count}...{Colors.ENDC}")
        
        try:
            # Build the context window
            final_prompt, usage_report = build_context_window(user_input, chat_history)
            
            # Show retrieval results
            print_retrieval_section(user_input)
            
            # Show token usage
            print_usage_report(usage_report)
            
            # Option to inspect full context
            show_context = input(f"\n{Colors.OKBLUE}Show full assembled context? (y/n):{Colors.ENDC} ").strip().lower()
            if show_context == 'y':
                print_assembled_context(final_prompt)
            
            # Generate a mock response
            print(f"\n{Colors.OKCYAN}Assistant (Mock Response):{Colors.ENDC}")
            print(f"  Based on the retrieved context, here's what I can tell you about Nyiko:\n")
            
            # Extract a simple response from the retrieval
            search_results = semantic_search(user_input, CV_DATA, top_k=3)
            if search_results:
                for doc, _ in search_results:
                    print(f"  • {doc}")
            
            print()
            
            # Update history
            chat_history += f"\nUser: {user_input}\nAssistant: [Response provided based on retrieved context]"
            
        except Exception as e:
            print(f"{Colors.FAIL}Error processing query: {e}{Colors.ENDC}\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--budget":
            print_header()
            print_budget_config()
        elif sys.argv[1] == "--help":
            print("Usage: python cli.py [options]")
            print("  (no args)   - Start interactive chat")
            print("  --budget    - Show budget configuration and exit")
            print("  --help      - Show this help message")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        interactive_chat()


if __name__ == "__main__":
    main()
