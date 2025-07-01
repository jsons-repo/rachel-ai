import os
import torch
from glob import glob
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset, Dataset
from rachel.core.config import get_config
from rachel.utils.common import analyze_training_jsonl
import argparse
import shutil

# === Parse arguments ===
parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, default="data", help="Path to folder containing training data")
parser.add_argument("--resume", action="store_true", help="Resume training if a checkpoint exists")
args = parser.parse_args()

PATH_TO_DATA = args.path
RESUME = args.resume

# === Run dataset stats ===
analyze_training_jsonl(PATH_TO_DATA)

# === Load config ===
cfg = get_config()

model_name = cfg.model.shallow_LLM.repo
trained_target = model_name.split("/")[-1].replace(".", "_")
output_dir = f"data/outputs/{trained_target}_lora"

# === Auto-resume logic ===
if not RESUME:
    print("🧹 Wiping previous output directory for a clean training run...")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

checkpoint_dirs = sorted(
    [f.path for f in os.scandir(output_dir) if f.is_dir() and f.name.startswith("checkpoint-")]
)
should_resume = RESUME or bool(checkpoint_dirs)

if should_resume:
    print(f"🔁 Resuming from checkpoint: {checkpoint_dirs[-1] if checkpoint_dirs else 'auto'}")
else:
    print("🔄 Starting fresh training run...")


# === Load dataset ===
print("📦 Loading dataset...")
dataset_paths = glob(f"{PATH_TO_DATA}/training/*/training_hf.jsonl")
dataset = load_dataset("json", data_files=dataset_paths)["train"]

print("Dataset:", dataset[0])
for i in range(3):
    print("--- Sample", i, "---")
    print("Prompt:", dataset[i]["prompt"][:200])
    print("Completion:", dataset[i]["completion"])


def tokenize(batch):
    full_texts = [
        f"{prompt.strip()}\n{completion.strip()}"
        for prompt, completion in zip(batch["prompt"], batch["completion"])
    ]
    return tokenizer(full_texts, truncation=True, max_length=2048, padding="max_length")




# === Load model + tokenizer ===
print("🧠 Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

print("tokenizer:", tokenizer(dataset[0]["prompt"] + "\n" + dataset[0]["completion"]))

# === Apply LoRA ===
print("🧪 Applying LoRA adapters...")
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)

# === Tokenize dataset ===
print("✍️ Tokenizing dataset...")
tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)

# === Setup training ===
print("🚀 Starting training setup...")
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    bf16=True,
    logging_dir=f"{output_dir}/logs",
    logging_steps=1,
    logging_first_step=True,
    save_strategy="epoch",
    save_total_limit=2,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

# === Train ===
print("🏋️ Training...")
if should_resume:
    trainer.train(resume_from_checkpoint=True)
else:
    trainer.train()

# === Save adapter model ===
adapter_dir = f"{output_dir}/adapter"
tokenizer_dir = f"{output_dir}/tokenizer"

print("💾 Saving adapter model...")
model.save_pretrained(adapter_dir)

print("💾 Saving tokenizer...")
tokenizer.save_pretrained(tokenizer_dir)

print("✅ Done.")
