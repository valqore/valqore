# Fine-Tuning a 7B Model for Cloud Security

Code examples from: **I Fine-Tuned a 7B Model to Be a Cloud Security Expert**

Read the full post: [I Fine-Tuned a 7B Model to Be a Cloud Security Expert — On My Local Machine, For $0](https://blog.valqore.io/i-fine-tuned-a-7b-model-to-be-a-cloud-security-expert-on-my-local-machine-for-0-ec77fe491703)

## Files

| File | Description |
|------|-------------|
| `training_config.py` | QLoRA fine-tuning configuration (hyperparameters only, not the training pipeline) |
| `data_generation_example.py` | How to generate training pairs from a rule engine |
| `eval_example.py` | Factual evaluation approach with substring checks |

## Context

These examples show the **approach** used to fine-tune Qwen 2.5 7B for infrastructure governance. The full training pipeline, dataset, and model weights are proprietary. These snippets are provided for educational purposes to illustrate the methodology described in the blog post.

## Key Results

- **Training time:** 43 minutes on RTX 5070 Ti (16GB VRAM)
- **Trainable parameters:** 40.4M / 4.4B (0.9%)
- **Adapter size:** 154 MB (GGUF)
- **Grade improvement:** B (73%) baseline to A (86%) fine-tuned
