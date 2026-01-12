#!/usr/bin/env python3
"""
Quick Start Script - Demonstrates the system in 3 stages

This script provides an interactive introduction to the Context-Window-Aware RAG System.
It guides you through:
1. Understanding the budget structure
2. Seeing budget overflow in action
3. Testing live queries

Run: python quickstart.py
"""

import sys
from test_demo import Colors
from assembler import build_context_window, CV_DATA
from rag_core import BUDGETS, count_tokens


def stage_1_understand_budgets():
    """Stage 1: Understand the budget structure."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}STAGE 1: Understanding Token Budgets{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    print(f"{Colors.OKBLUE}The Context-Window-Aware RAG System enforces strict token budgets{Colors.ENDC}")
    print(f"{Colors.OKBLUE}on 5 different sections of the context window.{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Budget Allocation:{Colors.ENDC}\n")
    
    total = sum(BUDGETS.values())
    for section, budget in sorted(BUDGETS.items(), key=lambda x: x[1], reverse=True):
        pct = (budget / total) * 100
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  {section.upper():15} {budget:5} tokens ({pct:5.1f}%) {bar}")
    
    print(f"\n  {Colors.OKGREEN}Total Budget: {total} tokens{Colors.ENDC}")
    print(f"\n{Colors.OKYELLOW}✓ This budget is safe for 4k-8k token context windows{Colors.ENDC}\n")


def stage_2_see_overflow():
    """Stage 2: See budget overflow handling."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}STAGE 2: Budget Overflow & Truncation{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    print(f"{Colors.OKBLUE}When a section exceeds its budget, content is truncated intelligently.{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Example: Instruction Overflow{Colors.ENDC}\n")
    
    # Create oversized instructions
    oversized = (
        "You are an advanced AI assistant representing Nyiko Shabangu. "
        "You must answer questions with extreme accuracy and clarity. "
        "Always be professional and provide detailed explanations. " * 10
    )
    
    from rag_core import smart_truncate
    
    original_tokens = count_tokens(oversized)
    budget = BUDGETS['instructions']
    truncated = smart_truncate(oversized, budget, "keep_start")
    final_tokens = count_tokens(truncated)
    
    print(f"  Original size:  {original_tokens} tokens")
    print(f"  Budget limit:   {budget} tokens")
    print(f"  After truncate: {final_tokens} tokens")
    print(f"  Reduction:      {original_tokens - final_tokens} tokens removed\n")
    
    print(f"{Colors.OKGREEN}✓ Truncated using 'keep_start' strategy{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Core persona definition preserved{Colors.ENDC}")
    print(f"  Preview: {truncated[:80]}...\n")


def stage_3_live_queries():
    """Stage 3: Test live queries."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}STAGE 3: Live Query Testing{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    sample_queries = [
        "Tell me about your AI experience.",
        "What are your cloud certifications?",
        "Describe your work with LLMs and RAG systems.",
    ]
    
    print(f"{Colors.OKBLUE}Processing {len(sample_queries)} sample queries...{Colors.ENDC}\n")
    
    chat_history = ""
    
    for idx, query in enumerate(sample_queries, 1):
        print(f"{Colors.BOLD}Query #{idx}: \"{Colors.OKCYAN}{query}{Colors.BOLD}\"{Colors.ENDC}")
        
        # Build context
        final_prompt, usage_report = build_context_window(query, chat_history)
        
        # Calculate metrics
        total_tokens = 0
        max_tokens = sum(BUDGETS.values())
        
        for section_name, content in usage_report.items():
            used = count_tokens(content)
            budget = BUDGETS[section_name]
            total_tokens += used
        
        pct = (total_tokens / max_tokens) * 100
        
        print(f"  Context size: {Colors.OKGREEN}{total_tokens}{Colors.ENDC} / {max_tokens} tokens ({pct:.1f}%)")
        
        # Check for truncations
        truncated_sections = []
        for section_name, content in usage_report.items():
            used = count_tokens(content)
            if used >= BUDGETS[section_name]:
                truncated_sections.append(section_name)
        
        if truncated_sections:
            print(f"  {Colors.FAIL}⚠️ Truncated: {', '.join(truncated_sections)}{Colors.ENDC}")
        else:
            print(f"  {Colors.OKGREEN}✓ All sections within budget{Colors.ENDC}")
        
        print()
        
        # Update history
        chat_history += f"\nUser: {query}\nAI: [Response provided]"


def stage_4_summary():
    """Stage 4: Summary and next steps."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Summary & Next Steps{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}✅ You've learned:{Colors.ENDC}\n")
    print("  1. How token budgets are structured across 5 sections")
    print("  2. How truncation works when budgets are exceeded")
    print("  3. How live queries are processed and assembled")
    print()
    
    print(f"{Colors.BOLD}Next steps:{Colors.ENDC}\n")
    print(f"  {Colors.OKCYAN}• Run the full test suite:{Colors.ENDC}")
    print(f"    {Colors.OKBLUE}python test_demo.py{Colors.ENDC}")
    print()
    print(f"  {Colors.OKCYAN}• Try the interactive CLI:{Colors.ENDC}")
    print(f"    {Colors.OKBLUE}python cli.py{Colors.ENDC}")
    print()
    print(f"  {Colors.OKCYAN}• View the web dashboard:{Colors.ENDC}")
    print(f"    {Colors.OKBLUE}streamlit run app.py{Colors.ENDC}")
    print()
    print(f"  {Colors.OKCYAN}• Read the technical guide:{Colors.ENDC}")
    print(f"    {Colors.OKBLUE}IMPLEMENTATION_GUIDE.md{Colors.ENDC}")
    print()


def main():
    """Run all stages."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Context-Window-Aware RAG System - Quick Start Guide  ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    print(f"{Colors.ENDC}\n")
    
    try:
        stage_1_understand_budgets()
        input(f"{Colors.OKBLUE}Press Enter to continue to Stage 2...{Colors.ENDC}")
        
        stage_2_see_overflow()
        input(f"{Colors.OKBLUE}Press Enter to continue to Stage 3...{Colors.ENDC}")
        
        stage_3_live_queries()
        input(f"{Colors.OKBLUE}Press Enter to see the summary...{Colors.ENDC}")
        
        stage_4_summary()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Quick Start Complete!{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKYELLOW}Quick start interrupted.{Colors.ENDC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
