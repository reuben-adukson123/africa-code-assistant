#!/usr/bin/env python3
"""
Build RAG index from local documentation
"""

import os
import sys
from pathlib import Path
import argparse
import json
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.rag_engine import RAGEngine
from src.utils.config import load_config


def setup_rag_index(docs_dir: str, output_dir: str):
    """Build RAG index from documentation files."""
    print("📚 Building RAG Index...")
    print("=========================")
    
    docs_path = Path(docs_dir)
    output_path = Path(output_dir)
    
    if not docs_path.exists():
        print(f"❌ Documents directory not found: {docs_dir}")
        print("   Creating sample documentation...")
        create_sample_docs(docs_path)
    
    # Load configuration
    config = load_config()
    
    # Override docs path
    config.set('docs_path', str(output_path))
    
    # Create RAG engine
    rag = RAGEngine(str(output_path), config)
    
    if rag.is_ready:
        print(f"✅ RAG index built successfully")
        print(f"   Documents: {len(rag.documents)} chunks")
        print(f"   Index saved to: {output_path}")
    else:
        print("❌ Failed to build RAG index")
        sys.exit(1)


def create_sample_docs(docs_path: Path):
    """Create sample documentation files."""
    docs_path.mkdir(parents=True, exist_ok=True)
    
    sample_docs = {
        'python.txt': """
Python is a high-level, interpreted programming language.
Key features include:
- Dynamic typing
- Automatic memory management
- Large standard library

Common built-in functions:
print() - Display output
len() - Get length of sequence
type() - Get type of object
list() - Create a list
dict() - Create a dictionary

Example:
def greet(name):
    return f"Hello, {name}!"
""",
        'pandas.txt': """
Pandas is a data manipulation library for Python.
Common operations:

Creating DataFrames:
import pandas as pd
df = pd.read_csv('data.csv')

Basic operations:
df.head() - View first rows
df.info() - Get data info
df.describe() - Get statistics
df.groupby() - Group data
df.merge() - Join DataFrames

Handling missing data:
df.dropna() - Remove missing values
df.fillna() - Fill missing values

Example:
df.groupby('category')['value'].mean()
""",
        'numpy.txt': """
NumPy is a numerical computing library for Python.
Core features:

Creating arrays:
import numpy as np
arr = np.array([1, 2, 3])
arr = np.zeros((3, 3))
arr = np.random.randn(5)

Common operations:
arr.mean() - Calculate mean
arr.std() - Calculate standard deviation
arr.min() - Get minimum
arr.max() - Get maximum
arr.sum() - Sum all values

Array manipulation:
arr.reshape() - Change shape
arr.transpose() - Transpose
np.concatenate() - Join arrays

Example:
np.linalg.inv() - Matrix inverse
"""
    }
    
    for filename, content in sample_docs.items():
        file_path = docs_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   Created: {filename}")
    
    print("✅ Sample documentation created")


def main():
    parser = argparse.ArgumentParser(description='Build RAG index for Africa Code Assistant')
    parser.add_argument(
        '--docs',
        default='./resources/docs',
        help='Documentation directory'
    )
    parser.add_argument(
        '--output',
        default='./resources/docs',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    setup_rag_index(args.docs, args.output)


if __name__ == "__main__":
    main()