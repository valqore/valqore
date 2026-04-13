"""Example QLoRA fine-tuning configuration for domain-specific LLM.

This shows the approach used to fine-tune Qwen 2.5 7B for infrastructure
governance. The full training pipeline is proprietary — this is the config only.
"""

TRAINING_CONFIG = {
    "base_model": "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    "method": "QLoRA",
    "lora_rank": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "epochs": 3,
    "batch_size": 2,
    "gradient_accumulation": 4,
    "learning_rate": 2e-4,
    "max_seq_length": 2048,
    "precision": "bf16",
    "warmup_ratio": 0.03,
}

# Results:
# Training time: 43 minutes on RTX 5070 Ti (16GB VRAM)
# Trainable parameters: 40.4M / 4.4B (0.9%)
# Adapter size: 154 MB (GGUF)
# Train loss: 3.44 → 0.15
# Eval loss: 0.260
# Grade: A (86%) vs B (73%) baseline
