"""
Configuration Management
"""

import os
import json
from pathlib import Path
from typing import Any, Dict

class AppConfig:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self.load()

    def load(self):
        # Check if config file exists in the current directory
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Loaded config from: {self.config_file}")
                print(f"   model_path: {self.config.get('model_path', 'NOT SET')}")
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                self.config = self.defaults()
        else:
            print(f"⚠️ Config file not found: {self.config_file}")
            print("   Using defaults...")
            self.config = self.defaults()
            self.save()

    def defaults(self) -> Dict:
        return {
            'ui': {'theme': 'darkly'},
            'language': 'en',
            'model_path': './models/qwen-coder-3b-q4/model-q4_0.gguf',
            'docs_path': './resources/docs',
            'llm': {
                'context_length': 4096,
                'batch_size': 512,
                'threads': 4
            },
            'rag': {
                'embedding_model': 'all-MiniLM-L6-v2',
                'chunk_size': 512,
                'overlap': 50
            }
        }

    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ Config saved to: {self.config_file}")
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")


def load_config():
    """Convenience function to load configuration."""
    return AppConfig()
