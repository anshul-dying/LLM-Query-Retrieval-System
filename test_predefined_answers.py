#!/usr/bin/env python3

from core.predefined_answers import PredefinedAnswers
from core.decision_engine import DecisionEngine

def test_predefined_answers():
    """Test the predefined answers system"""
    print("🧪 Testing Predefined Answers System (Query-Only Matching)")
    print("=" * 60)
    
    # Test predefined answers loading
    predefined = PredefinedAnswers()
    
    print(f"\n📊 Loaded {len(predefined.get_all_predefined_qa())} predefined Q&A pairs")
    
    # Test exact matches (no document name needed)
    test_cases = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the ideal spark plug gap recommeded",
        "What is the official name of India according to Article 1 of the Constitution?"
    ]
    
    print(f"\n✅ Testing Exact Matches:")
    for query in test_cases:
        answer = predefined.find_matching_answer(query)
        if answer:
            print(f"   ✓ Found answer for: '{query[:50]}...'")
            print(f"      Answer: {answer[:100]}...")
        else:
            print(f"   ✗ No answer found for: '{query[:50]}...'")
    
    # Test fuzzy matches
    fuzzy_test_cases = [
        "What is the grace period?",  # Shorter version
        "spark plug gap",  # Partial match
        "India's official name"  # Similar meaning
    ]
    
    print(f"\n🔍 Testing Fuzzy Matches:")
    for query in fuzzy_test_cases:
        answer = predefined.find_matching_answer(query, similarity_threshold=0.6)
        if answer:
            print(f"   ✓ Found fuzzy match for: '{query[:50]}...'")
            print(f"      Answer: {answer[:100]}...")
        else:
            print(f"   ✗ No fuzzy match found for: '{query[:50]}...'")
    
    # Test decision engine integration
    print(f"\n🤖 Testing Decision Engine Integration:")
    decision_engine = DecisionEngine()
    
    test_queries = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the ideal spark plug gap recommeded",
        "What is the official name of India according to Article 1 of the Constitution?",
        "This is a completely new question that should use LLM"  # Should use LLM
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n   Query {i+1}: {query[:60]}...")
        answers = decision_engine.process_queries([query])  # No doc_name needed
        if answers:
            print(f"      Answer: {answers[0][:100]}...")
        else:
            print(f"      No answer generated")

def test_query_matching():
    """Test query matching scenarios"""
    print(f"\n🔍 Testing Query Matching Scenarios")
    print("=" * 50)
    
    predefined = PredefinedAnswers()
    
    # Test various query formats
    test_scenarios = [
        ("What is the grace period?", "grace period premium payment"),  # Similar meaning
        ("spark plug gap", "What is the ideal spark plug gap recommeded"),  # Partial match
        ("India official name", "What is the official name of India according to Article 1 of the Constitution?"),  # Similar
        ("completely different question", "This should not match anything")  # No match
    ]
    
    for test_query, expected_query in test_scenarios:
        print(f"\n   Testing: '{test_query}'")
        answer = predefined.find_matching_answer(test_query, similarity_threshold=0.6)
        if answer:
            print(f"      ✓ Found match!")
            print(f"      Answer: {answer[:80]}...")
        else:
            print(f"      ✗ No match found")

if __name__ == "__main__":
    test_predefined_answers()
    test_query_matching() 