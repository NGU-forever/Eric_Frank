#!/usr/bin/env python3
"""
Manage RAG Knowledge Base

Usage:
    python manage_knowledge.py add --text "content" --source "filename"
    python manage_knowledge.py query --text "question"
    python manage_knowledge.py clear
"""
import sys
import os
import argparse
import asyncio
from typing import Dict, Any

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.skills.skill_rag import RagSkill
from app.core.context import ExecutionContext

async def main():
    parser = argparse.ArgumentParser(description="Manage Knowledge Base")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add content to knowledge base")
    add_parser.add_argument("--text", required=True, help="Text content to add")
    add_parser.add_argument("--source", default="manual", help="Source metadata")
    add_parser.add_argument("--collection", default="default", help="Collection name")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query knowledge base")
    query_parser.add_argument("--text", required=True, help="Query text")
    query_parser.add_argument("--collection", default="default", help="Collection name")
    query_parser.add_argument("--top-k", type=int, default=3, help="Number of results")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear knowledge base")
    clear_parser.add_argument("--collection", default="default", help="Collection name")
    
    args = parser.parse_args()
    
    # Initialize Skill
    skill = RagSkill()
    context = ExecutionContext(input_data={})
    
    if args.command == "add":
        print(f"Adding to collection '{args.collection}'...")
        result = await skill.execute(
            context,
            action="add",
            text=args.text,
            collection_name=args.collection,
            metadata={"source": args.source}
        )
        print(result)
        
    elif args.command == "query":
        print(f"Querying collection '{args.collection}'...")
        result = await skill.execute(
            context,
            action="query",
            text=args.text,
            collection_name=args.collection,
            top_k=args.top_k
        )
        
        if result.get("success"):
            print(f"\nFound {len(result.get('documents', []))} results:\n")
            for i, doc in enumerate(result.get("documents", [])):
                print(f"--- Result {i+1} (Score: {doc['score']:.4f}) ---")
                print(f"Source: {doc['metadata'].get('source')}")
                print(f"Content: {doc['content'][:200]}...")
                print()
        else:
            print("Error:", result.get("message"))
            
    elif args.command == "clear":
        print(f"Clearing collection '{args.collection}'...")
        result = await skill.execute(
            context,
            action="clear",
            collection_name=args.collection
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
