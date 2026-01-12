#!/usr/bin/env python3
"""
Test Vector Search vs Keyword Search
Demonstrates ChromaDB semantic matching with sentence-transformers embeddings
"""

from assembler import semantic_search, keyword_search, CV_DATA, CHROMADB_AVAILABLE
from rag_core import count_tokens

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def test_vector_search():
    """Test ChromaDB vector search"""
    print_section("TEST 1: Vector Search (Semantic Similarity)")
    
    print(f"{Colors.OKGREEN}✅ ChromaDB Status: {'Available' if CHROMADB_AVAILABLE else 'Not Available'}{Colors.ENDC}\n")
    
    test_queries = [
        "Tell me about your AI experience",
        "What cloud technologies do you know",
        "Your work at GotBot AI",
        "Educational background",
        "Python and development skills",
    ]
    
    for query in test_queries:
        print(f"{Colors.BOLD}Query: {query}{Colors.ENDC}")
        results = semantic_search(query, top_k=3)
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"  [{i}] Score: {score:.3f} | Tokens: {count_tokens(doc):3}")
            print(f"      {doc[:65]}{'...' if len(doc) > 65 else ''}")
        print()


def compare_search_methods():
    """Compare vector search vs keyword search"""
    print_section("TEST 2: Vector vs Keyword Search Comparison")
    
    query = "artificial intelligence and deep learning"
    top_k = 3
    
    print(f"Query: {Colors.BOLD}{query}{Colors.ENDC}\n")
    
    # Vector search
    print(f"{Colors.OKGREEN}VECTOR SEARCH (ChromaDB + all-MiniLM-L6-v2):{Colors.ENDC}")
    vector_results = semantic_search(query, top_k=top_k)
    for i, (doc, score) in enumerate(vector_results, 1):
        print(f"  [{i}] Similarity: {score:.3f} | {doc[:55]}...")
    
    # Keyword search
    print(f"\n{Colors.OKYELLOW}KEYWORD SEARCH (Fallback):{Colors.ENDC}")
    keyword_results = keyword_search(query, CV_DATA, top_k=top_k)
    for i, (doc, score) in enumerate(keyword_results, 1):
        print(f"  [{i}] Score: {score:.0f} keywords | {doc[:55]}...")
    
    print(f"\n{Colors.OKBLUE}Key Difference:{Colors.ENDC}")
    print("  • Vector Search: Understands semantic meaning (\"AI\" ≈ \"artificial intelligence\")")
    print("  • Keyword Search: Simple term matching (requires exact keywords)")


def test_embedding_quality():
    """Demonstrate embedding quality"""
    print_section("TEST 3: Semantic Understanding Examples")
    
    semantic_queries = [
        ("AWS expertise", "cloud experience"),
        ("Python coding", "software development"),
        ("machine learning", "deep neural networks"),
        ("job interview", "hiring process"),
    ]
    
    print(f"{Colors.OKBLUE}Vector search finds semantically similar documents:{Colors.ENDC}\n")
    
    for query1, query2 in semantic_queries:
        print(f"Query 1: {Colors.BOLD}{query1}{Colors.ENDC}")
        results1 = semantic_search(query1, top_k=1)
        if results1:
            print(f"  → {results1[0][0][:60]}...")
        
        print(f"Query 2: {Colors.BOLD}{query2}{Colors.ENDC}")
        results2 = semantic_search(query2, top_k=1)
        if results2:
            print(f"  → {results2[0][0][:60]}...")
        print()


def test_corpus_coverage():
    """Show all documents in the corpus"""
    print_section("TEST 4: Knowledge Base Coverage")
    
    print(f"Total documents in CV corpus: {Colors.BOLD}{len(CV_DATA)}{Colors.ENDC}\n")
    print(f"Embedding model: {Colors.OKGREEN}all-MiniLM-L6-v2 (384 dimensions){Colors.ENDC}\n")
    
    for i, doc in enumerate(CV_DATA, 1):
        tokens = count_tokens(doc)
        print(f"  [{i}] ({tokens} tokens) {doc[:65]}{'...' if len(doc) > 65 else ''}")
    
    total_tokens = sum(count_tokens(doc) for doc in CV_DATA)
    print(f"\n{Colors.BOLD}Total tokens in corpus: {total_tokens}{Colors.ENDC}")


if __name__ == "__main__":
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 Vector Search Testing Suite (ChromaDB)                ║")
    print("║  Demonstrating Semantic Search with Embeddings           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    test_vector_search()
    compare_search_methods()
    test_embedding_quality()
    test_corpus_coverage()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ All tests completed!{Colors.ENDC}\n")
