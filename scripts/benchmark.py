#!/usr/bin/env python3
"""
Benchmark the performance of the Africa Code Assistant
"""

import os
import sys
import time
import json
import psutil
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.llm_engine import LLMEngine
from src.utils.config import load_config


def benchmark_llm(model_path: str, num_runs: int = 5):
    """Benchmark the LLM engine."""
    print("🚀 Running Benchmarks...")
    print("=========================")
    
    config = load_config()
    
    # Initialize LLM
    print(f"📥 Loading model: {model_path}")
    llm = LLMEngine(model_path, config)
    
    # Test prompts
    prompts = [
        "Write a Python function to calculate factorial.",
        "Explain what a class is in object-oriented programming.",
        "Write a simple HTML page with a button.",
        "What is a list comprehension in Python?",
        "Write a SQL query to join two tables."
    ]
    
    results = []
    
    print(f"\n📊 Running {num_runs} benchmarks...")
    print("-" * 50)
    
    for i in range(num_runs):
        print(f"\nRun {i+1}/{num_runs}")
        run_result = {}
        
        for prompt in prompts[:3]:  # Test first 3 prompts
            # Measure generation time
            start_time = time.time()
            response = llm.generate(prompt, max_tokens=200)
            elapsed = time.time() - start_time
            
            # Calculate tokens
            tokens = len(response.split())
            speed = tokens / elapsed if elapsed > 0 else 0
            
            # Get memory usage
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            
            run_result[prompt[:30]] = {
                'response_length': len(response),
                'tokens': tokens,
                'time': elapsed,
                'speed': speed,
                'memory_mb': memory_mb
            }
            
            print(f"  ✓ Generated {tokens} tokens in {elapsed:.2f}s ({speed:.1f} tokens/s)")
        
        results.append(run_result)
    
    # Calculate averages
    avg_speed = 0
    avg_time = 0
    avg_memory = 0
    count = 0
    
    for run in results:
        for result in run.values():
            avg_speed += result['speed']
            avg_time += result['time']
            avg_memory += result['memory_mb']
            count += 1
    
    avg_speed /= count
    avg_time /= count
    avg_memory /= count
    
    print("\n📊 Summary")
    print("-" * 50)
    print(f"Average speed: {avg_speed:.1f} tokens/second")
    print(f"Average time: {avg_time:.2f} seconds")
    print(f"Average memory: {avg_memory:.1f} MB")
    
    # Save results
    results_file = Path("benchmark_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'model': model_path,
            'num_runs': num_runs,
            'averages': {
                'speed': avg_speed,
                'time': avg_time,
                'memory_mb': avg_memory
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {results_file}")
    
    # Cleanup
    llm.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Benchmark Africa Code Assistant')
    parser.add_argument(
        '--model',
        default='./models/qwen-coder-3b-q4/model-q4_K_M.gguf',
        help='Path to model file'
    )
    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of benchmark runs'
    )
    
    args = parser.parse_args()
    
    benchmark_llm(args.model, args.runs)


if __name__ == "__main__":
    main()
