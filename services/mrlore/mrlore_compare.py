#!/usr/bin/env python3
"""
MrLore Compare Mode - Automatically run the same query across multiple models
and print side-by-side output for grading and optimization.
"""

import argparse
import time
from mrlore import MrLore

DEFAULT_MODELS = [
    "phi3:3.8b",
    "llama3:8b",
    "dolphin3:8b",
    "mistral-nemo:12b",
    "qwen2.5:7b-instruct"
]

def main():
    parser = argparse.ArgumentParser(
        description="MrLore Compare Mode - Run one query across multiple models"
    )
    parser.add_argument("--query", "-q", required=True, help="Query to run")
    parser.add_argument("--models", "-m", nargs="+", default=DEFAULT_MODELS,
                        help="List of models to test")
    parser.add_argument("--chapters", "-c", default="chapters", help="Chapters directory")

    args = parser.parse_args()
    print(f"🎯 Comparing models for query: {args.query}")
    print(f"📚 Chapters: {args.chapters}")
    print("=" * 60)

    for model in args.models:
        print(f"\n🤖 Model: {model}")
        print("-" * 60)
        try:
            lore = MrLore(chapters_dir=args.chapters, model=model)
            start = time.time()
            result = lore.query(args.query)
            elapsed = time.time() - start
            print(f"🕒 Time: {elapsed:.1f}s")
            print(f"💬 Output:\n{result[:2000]}\n...")
        except Exception as e:
            print(f"❌ Error with model {model}: {e}")
        print("=" * 60)

if __name__ == "__main__":
    main()
