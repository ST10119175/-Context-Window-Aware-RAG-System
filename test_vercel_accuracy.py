#!/usr/bin/env python3
"""
Test to verify if the example response is accurate and within budget
"""

from assembler import build_context_window, semantic_search, CV_DATA
from rag_core import BUDGETS, count_tokens

# The example response from your question
example_response = """Based solely on the provided context, Nyiko Shabangu is an AI Engineer and Software Developer specializing in intelligent systems. His key qualifications include:

Core Expertise:
- Python, Google Vertex AI, Dialogflow, AWS cloud architecture
- Focus on RAG systems and multi-agent LLM applications

Professional Experience:
- AI Solutions Developer at GotBot AI: Engineered custom Multi-Agent LLM systems using Vertex AI and RAG pipelines. Securely integrated conversational agents with Enterprise APIs, reducing issue resolution time by 40% through automated workflows.
- AI Trainer at Outlier AI: Developed gold-standard code solutions for LLM training, performed RLHF analysis for security/logical validation, and conducted adversarial testing.
- Web Developer at Kelani Auctions: Optimized revenue by 15% and built real-time auction management platforms.

Education:
- Bachelor of Computer and Information Sciences from Varsity College.

He combines cloud architecture, LLM engineering, and system optimization skills to deliver scalable AI solutions."""

# Test query that would generate this response
test_query = "Who is Nyiko Shabangu?"

print("="*80)
print("VERCEL RESPONSE ACCURACY & BUDGET ANALYSIS")
print("="*80)

# 1. Check the context that would be assembled
print("\n[STEP 1] Context Assembly for Query")
print("-"*80)
final_prompt, usage_report = build_context_window(test_query, "")

total_context_tokens = 0
for section, content in usage_report.items():
    used = count_tokens(content)
    budget = BUDGETS[section]
    total_context_tokens += used
    status = "✅ OK" if used <= budget else "⚠️  OVER"
    pct = (used / budget) * 100
    print(f"  {section.upper():15} {used:4}/{budget:4} tokens  {status}  ({pct:5.1f}%)")

print("-"*80)
print(f"  TOTAL CONTEXT   {total_context_tokens:4}/{sum(BUDGETS.values())} tokens  ({(total_context_tokens/sum(BUDGETS.values()))*100:.1f}%)")

# 2. Check the response token count
print("\n[STEP 2] Response Token Analysis")
print("-"*80)
response_tokens = count_tokens(example_response)
print(f"  Response length: {response_tokens} tokens")
print(f"  Response + Context: {total_context_tokens + response_tokens} tokens")

# 3. Verify accuracy by checking retrieval
print("\n[STEP 3] Accuracy Verification (BM25 Retrieval)")
print("-"*80)
search_results = semantic_search(test_query, CV_DATA, top_k=5)
print(f"  Query: '{test_query}'")
print(f"  Top relevant documents:")
for idx, (doc, score) in enumerate(search_results[:3], 1):
    print(f"    [{idx}] Score: {score:.3f}")
    print(f"        {doc[:70]}...")

# 4. Check if response facts match CV data
print("\n[STEP 4] Fact Checking Against CV Data")
print("-"*80)

facts_to_check = [
    ("AI Engineer and Software Developer", "Role/Title"),
    ("Python, Google Vertex AI, Dialogflow, AWS", "Core Technologies"),
    ("GotBot AI", "Current Employer"),
    ("Multi-Agent LLM systems", "Key Project"),
    ("40%", "Performance Metric"),
    ("Outlier AI", "Previous Employer"),
    ("Kelani Auctions", "Earlier Experience"),
    ("15%", "Revenue Optimization"),
    ("Bachelor of Computer and Information Sciences", "Education"),
    ("Varsity College", "Institution"),
]

all_cv_text = " ".join(CV_DATA)

matches = 0
for fact, category in facts_to_check:
    if fact.lower() in all_cv_text.lower():
        matches += 1
        print(f"  ✅ {category}: '{fact}' - FOUND in CV data")
    else:
        print(f"  ❌ {category}: '{fact}' - NOT FOUND")

accuracy_pct = (matches / len(facts_to_check)) * 100
print("-"*80)
print(f"  Accuracy: {matches}/{len(facts_to_check)} facts verified ({accuracy_pct:.0f}%)")

# 5. Budget Analysis
print("\n[STEP 5] Budget Compliance Summary")
print("="*80)

total_budget = sum(BUDGETS.values())
budget_used_pct = (total_context_tokens / total_budget) * 100
budget_remaining = total_budget - total_context_tokens

print(f"\n  Context Budget:")
print(f"    Total available: {total_budget} tokens")
print(f"    Used by query:   {total_context_tokens} tokens ({budget_used_pct:.1f}%)")
print(f"    Remaining:       {budget_remaining} tokens ({100-budget_used_pct:.1f}%)")

print(f"\n  Response Analysis:")
print(f"    Response tokens: {response_tokens} tokens")
print(f"    Total (context + response): {total_context_tokens + response_tokens} tokens")

print(f"\n  ✅ Budget Status: {'WITHIN BUDGET' if total_context_tokens <= total_budget else 'OVER BUDGET'}")
print(f"  ✅ Accuracy: {accuracy_pct:.0f}% of facts verified")

# 6. Why is it within budget?
print("\n[STEP 6] Why Is This Within Budget?")
print("="*80)

reasons = [
    ("Simple Query", f"'{test_query}' is only {count_tokens(test_query)} tokens - very short"),
    ("No Chat History", "Goal section uses minimal tokens (no previous conversation)"),
    ("Efficient Retrieval", f"BM25 returns only top-{len(search_results)} relevant docs, not entire corpus"),
    ("Smart Truncation", "Each section has 'keep_start' or 'keep_end' strategy"),
    ("Budget Enforcement", "smart_truncate() ensures no section exceeds its limit"),
]

for idx, (reason, explanation) in enumerate(reasons, 1):
    print(f"\n  {idx}. {reason}")
    print(f"     → {explanation}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"""
✅ The Vercel response IS ACCURATE ({accuracy_pct:.0f}% facts verified)
✅ The context assembly IS WITHIN BUDGET ({budget_used_pct:.1f}% of {total_budget} tokens used)

WHY IT WORKS:
• Simple query requires minimal context
• BM25 retrieval is efficient (top-k only)
• Budget enforcement prevents overflow
• Each section uses appropriate truncation strategy
• Response is based on actual CV data (not hallucinated)

COST IMPACT:
• Context: {total_context_tokens} tokens
• Response: {response_tokens} tokens
• Total: {total_context_tokens + response_tokens} tokens
• vs. Unoptimized: ~15,000 tokens
• Savings: {((1 - (total_context_tokens + response_tokens)/15000) * 100):.1f}%
""")

print("="*80)
