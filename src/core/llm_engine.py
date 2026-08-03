"""
LLM Inference Engine using llama-cpp-python
"""

import os
import time
from pathlib import Path
import psutil
from llama_cpp import Llama

# Use absolute import
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMEngine:
    """LLM inference engine with memory management."""
    
    # Supported programming languages for translation
    SUPPORTED_LANGUAGES = [
        'python', 'java', 'javascript', 'cpp', 'csharp', 
        'php', 'ruby', 'go', 'rust', 'sql'
    ]
    
    def __init__(self, model_path: str, config):
        """Initialize the LLM engine."""
        self.config = config
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        self.is_processing = False
        self.context_length = config.get('llm.context_length', 4096)
        self.batch_size = config.get('llm.batch_size', 512)
        self.threads = config.get('llm.threads', 4)
        self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load the LLM model."""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found: {model_path}")
            logger.info(f"Loading model from {model_path}")
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            logger.info(f"Current memory usage: {memory_mb:.1f} MB")
            self.model = Llama(
                model_path=model_path,
                n_ctx=self.context_length,
                n_batch=self.batch_size,
                n_threads=self.threads,
                n_gpu_layers=0,
                verbose=False,
                seed=42,
                f16_kv=True,
                logits_all=False,
                embedding=False
            )
            self.is_loaded = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate text from the model."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        try:
            self.is_processing = True
            start_time = time.time()
            output = self.model(
                prompt, max_tokens=max_tokens, temperature=temperature,
                top_p=0.9, top_k=40, repeat_penalty=1.1,
                stop=["\n\n\n", "Human:", "User:"], echo=False, stream=False
            )
            if isinstance(output, dict) and 'choices' in output:
                response = output['choices'][0]['text'].strip()
            else:
                response = str(output)
            elapsed = time.time() - start_time
            tokens = len(response.split())
            speed = tokens / elapsed if elapsed > 0 else 0
            logger.info(f"Generated {tokens} tokens in {elapsed:.2f}s ({speed:.1f} tokens/s)")
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
        finally:
            self.is_processing = False
    
    def chat(self, message: str) -> str:
        """Chat with the model."""
        prompt = f"User: {message}\n\nAssistant: "
        return self.generate(prompt, max_tokens=512, temperature=0.7)
    
    def generate_code(self, prompt: str, language: str) -> str:
        """Generate code in the specified language."""
        system_prompt = f"You are an expert {language} programmer. Generate clean, efficient code. Provide only the code, no explanations."
        full_prompt = f"{system_prompt}\n\nTask: {prompt}\n\nCode:\n```{language}\n"
        return self.generate(full_prompt, max_tokens=1024, temperature=0.3)
    
    def explain_code(self, prompt: str, code: str) -> str:
        """Explain the provided code."""
        system_prompt = "You are a programming instructor. Explain code in clear, simple terms."
        full_prompt = f"{system_prompt}\n\nCode:\n```\n{code}\n```\n\nExplanation:"
        return self.generate(full_prompt, max_tokens=1024, temperature=0.5)
    
    def debug_code(self, prompt: str, code: str) -> str:
        """Debug the provided code."""
        system_prompt = "You are a debugging expert. Identify bugs, explain why they occur, and provide fixes."
        full_prompt = f"{system_prompt}\n\nCode with bugs:\n```\n{code}\n```\n\nDebug analysis:"
        return self.generate(full_prompt, max_tokens=1024, temperature=0.4)
    
    def optimize_code(self, prompt: str, code: str) -> str:
        """Optimize the provided code."""
        system_prompt = "You are a code optimization expert. Improve performance, readability, and maintainability."
        full_prompt = f"{system_prompt}\n\nOriginal code:\n```\n{code}\n```\n\nOptimized code:"
        return self.generate(full_prompt, max_tokens=1024, temperature=0.3)
    
    def translate_code(self, prompt: str, code: str, target_lang: str) -> str:
        """Translate code between programming languages."""
        system_prompt = f"You are a code translator. Convert the provided code to {target_lang}. Follow language best practices."
        full_prompt = f"{system_prompt}\n\nOriginal code:\n```\n{code}\n```\n\nTranslated code ({target_lang}):\n```{target_lang}\n"
        return self.generate(full_prompt, max_tokens=1024, temperature=0.3)
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in MB."""
        return psutil.Process().memory_info().rss // 1024 // 1024
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_loaded = False
        self.model = None
        logger.info("Model resources cleaned up")