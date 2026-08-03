#!/usr/bin/env python3
"""
Download and quantize LLM models for the Africa Code Assistant
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import requests
import json


# Define model configurations at the top level so they're accessible everywhere
MODEL_CONFIGS = {
    'qwen-coder-3b-q4': {
        'url': 'https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/qwen2.5-coder-3b-instruct-q4_0.gguf',
        'filename': 'model-q4_0.gguf',
        'size_gb': 1.8
    },
    'qwen-coder-3b-q8': {
        'url': 'https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/qwen2.5-coder-3b-instruct-q8_0.gguf',
        'filename': 'model-q8_0.gguf',
        'size_gb': 3.2
    },
    'phi-3-mini-q4': {
        'url': 'https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_K_M.gguf',
        'filename': 'phi-3-mini-q4.gguf',
        'size_gb': 2.3
    },
    'tinyllama-q4': {
        'url': 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
        'filename': 'tinyllama-q4.gguf',
        'size_gb': 0.6
    }
}


def download_model(model_name: str, output_dir: str):
    """Download a model from Hugging Face."""
    model_dir = Path(output_dir) / model_name
    model_dir.mkdir(parents=True, exist_ok=True)
    
    config = MODEL_CONFIGS.get(model_name)
    if not config:
        print(f"? Unknown model: {model_name}")
        print(f"Available models: {', '.join(MODEL_CONFIGS.keys())}")
        sys.exit(1)
    
    output_file = model_dir / config['filename']
    
    # Check if file already exists
    if output_file.exists():
        file_size_mb = output_file.stat().st_size // 1024 // 1024
        expected_size_mb = config['size_gb'] * 1024
        if file_size_mb >= expected_size_mb * 0.9:  # Allow 10% tolerance
            print(f"? Model already exists: {output_file}")
            print(f"   Size: {file_size_mb} MB")
            return str(output_file)
        else:
            print(f"??  Existing file is incomplete ({file_size_mb} MB / {expected_size_mb:.0f} MB)")
            print("   Re-downloading...")
            output_file.unlink()  # Delete incomplete file
    
    print(f"?? Downloading {model_name} ({config['size_gb']} GB)")
    print(f"   This may take a while...")
    
    try:
        # Download using requests with progress bar
        response = requests.get(config['url'], stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        block_size = 8192
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Show progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded // 1024 // 1024
                        mb_total = total_size // 1024 // 1024
                        print(f"\r   Progress: {percent:.1f}% ({mb_downloaded} MB / {mb_total} MB)", end='', flush=True)
        
        print(f"\n? Model downloaded to: {output_file}")
        print(f"   Size: {output_file.stat().st_size // 1024 // 1024} MB")
        return str(output_file)
        
    except Exception as e:
        print(f"\n? Download failed: {e}")
        # Clean up partial download
        if output_file.exists():
            output_file.unlink()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Download LLM model for Africa Code Assistant')
    parser.add_argument(
        '--model',
        default='qwen-coder-3b-q4',
        choices=list(MODEL_CONFIGS.keys()),
        help='Model to download'
    )
    parser.add_argument(
        '--output',
        default='./models',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    print("?? Africa Code Assistant - Model Downloader")
    print("===========================================")
    
    download_model(args.model, args.output)
    
    print("\n?? Next steps:")
    print("1. Update model path in config.json")
    config = MODEL_CONFIGS[args.model]
    print(f"   'model_path': './models/{args.model}/{config['filename']}'")
    print("2. Run: python src/main.py")


if __name__ == "__main__":
    main()