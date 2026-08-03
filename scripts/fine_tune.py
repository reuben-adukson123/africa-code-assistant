#!/usr/bin/env python3
"""
Fine-tune a model on African language code data
"""

import os
import sys
import json
import argparse
from pathlib import Path

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import transformers

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def prepare_dataset(data_file: str):
    """Prepare dataset for fine-tuning."""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Format data for training
    texts = []
    for item in data:
        if 'code' in item and 'explanation' in item:
            text = f"### Code:\n{item['code']}\n\n### Explanation:\n{item['explanation']}"
            texts.append(text)
    
    return Dataset.from_dict({'text': texts})


def fine_tune_model(
    model_name: str,
    dataset_file: str,
    output_dir: str,
    num_epochs: int = 3
):
    """Fine-tune a model."""
    print("🚀 Starting Fine-tuning...")
    print("===========================")
    
    # Load model and tokenizer
    print(f"📥 Loading model: {model_name}")
    
    # Use 4-bit quantization for memory efficiency
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Prepare dataset
    print(f"📚 Loading dataset: {dataset_file}")
    dataset = prepare_dataset(dataset_file)
    tokenized_dataset = dataset.map(
        lambda x: tokenizer(x['text'], truncation=True, padding='max_length', max_length=512),
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="steps",
        eval_steps=100,
        save_total_limit=3,
        load_best_model_at_end=True,
        learning_rate=2e-4,
        bf16=True,
        max_grad_norm=0.3,
        weight_decay=0.001,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train
    print("🏋️ Starting Training...")
    trainer.train()
    
    # Save model
    print(f"💾 Saving model to: {output_dir}")
    trainer.save_model()
    
    print("✅ Fine-tuning complete!")
    print(f"   Model saved to: {output_dir}")
    
    # Save adapter config
    model.save_pretrained(output_dir)


def main():
    parser = argparse.ArgumentParser(description='Fine-tune model for Africa Code Assistant')
    parser.add_argument(
        '--model',
        default='Qwen/Qwen2.5-Coder-3B-Instruct',
        help='Base model name'
    )
    parser.add_argument(
        '--data',
        required=True,
        help='Training data JSON file'
    )
    parser.add_argument(
        '--output',
        default='./fine_tuned_model',
        help='Output directory'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Number of training epochs'
    )
    
    args = parser.parse_args()
    
    fine_tune_model(args.model, args.data, args.output, args.epochs)


if __name__ == "__main__":
    main()