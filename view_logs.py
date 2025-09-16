#!/usr/bin/env python3

import os
import json
from datetime import datetime
from core.logger_manager import LoggerManager

def view_logs():
    """View logs in a readable format"""
    logger_manager = LoggerManager()
    
    print("=" * 80)
    print("📊 ANALYTICS DASHBOARD")
    print("=" * 80)
    
    # Get summary
    try:
        links = logger_manager.get_document_links()
        queries = logger_manager.get_all_queries()
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Documents: {len(links)}")
        print(f"   Total Queries: {len(queries)}")
        print(f"   Average Queries per Document: {len(queries) / len(links) if links else 0:.1f}")
        
        # Show recent documents
        print(f"\n📄 RECENT DOCUMENTS:")
        for link in links[-5:]:  # Show last 5 documents
            timestamp = datetime.fromisoformat(link['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"   [{timestamp}] ID: {link['doc_id']} | {link['filename']}")
            print(f"      URL: {link['document_url'][:80]}...")
        
        # Show recent queries
        print(f"\n❓ RECENT QUERIES:")
        for query in queries[-10:]:  # Show last 10 queries
            timestamp = datetime.fromisoformat(query['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"   [{timestamp}] Doc ID: {query['doc_id']}")
            print(f"      Q: {query['query'][:60]}...")
            print(f"      A: {query['response'][:60]}...")
            print()
        
    except Exception as e:
        print(f"Error reading logs: {e}")

def view_document_queries(doc_id: int):
    """View queries for a specific document"""
    logger_manager = LoggerManager()
    
    print(f"\n📋 QUERIES FOR DOCUMENT ID: {doc_id}")
    print("=" * 80)
    
    queries = logger_manager.get_queries_for_document(doc_id)
    
    if not queries:
        print("No queries found for this document.")
        return
    
    for i, query in enumerate(queries, 1):
        timestamp = datetime.fromisoformat(query['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{i}. [{timestamp}]")
        print(f"   Question: {query['query']}")
        print(f"   Answer: {query['response']}")
        print("-" * 40)

def export_logs_to_json():
    """Export logs to JSON format"""
    logger_manager = LoggerManager()
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "links": logger_manager.get_document_links(),
        "queries": logger_manager.get_all_queries()
    }
    
    with open("logs_export.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Logs exported to logs_export.json")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "export":
            export_logs_to_json()
        elif sys.argv[1].isdigit():
            view_document_queries(int(sys.argv[1]))
        else:
            print("Usage: python view_logs.py [doc_id|export]")
    else:
        view_logs() 