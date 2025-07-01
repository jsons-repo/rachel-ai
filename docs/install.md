# Installation

[Installation](install.md)

[Configure LAN setup](lan_setup.md)

[Getting Started](getting_started.md)

[How It Works](how_it_works.md)

[config.yaml Reference](docs/config.md)

### 1. Clone the Repo

```bash
git clone https://github.com/jsons-repo/rachel-ai.git
cd rachel
```

### 2. Create a Virtual Environment

> `Python 3.10` or higher recommended
From your project root

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e . # (default with CUDA)
```
This will install all required packages as defined in `pyproject.toml`, including the core dependencies for real-time transcription, semantic/embedded filtering, LLM-based summarization, and server functionality.

#### Backend Auto-Detection

The app supports multiple backends (CUDA, Metal, CPU) and will auto-detect the best option for your system at runtime:

- On **Apple Silicon**, it prefers Metal via `mlx` and `mlx-whisper` if installed.
- On **Linux with NVIDIA GPUs**, it can use `faster-whisper` or `whispercpp` with CUDA support.
- On **CPU-only systems**, it will still work, just way slower (not really real-time)

Optionally: If you want to explicitly install hardware-optimized dependencies:
```bash
pip install -e '.[train]' # training
pip install -e '.[metal]' # Apple Silicon
```

### 4. API Keys and Configuring your Models

The app comes with a known-good default configuration in `config.yaml` that should "just work" on CUDA machines but the models are not pre-downloaded. Instead, whatever is in your `config.yaml` will be downloaded automatically at runtime and saved to `.rachel/models` but you'll need to provide any API keys required to access the target repos.

> Lots models of free models at [Hugging Face](https://huggingface.co).

Add your API credentials in a `.env` file at the project root:

  ```env
    HF_TOKEN=your_huggingface_token
    DEEP_API_KEY=your_openai_or_claude_key
  ```
  - `HF_TOKEN` is required for downloading models from Hugging Face (make sure you have access to any gated models you use)

  - `DEEP_API_KEY` is used for deep model queries (e.g., OpenAI)

> ⚠️ Make sure you **do not commit your `.env` file** to version control.

#### Local Transcription Model
Used to convert microphone input into text.
```yaml
model:
  transcription:
    repo: "guillaumekln/faster-whisper-small"
    name: null
    backend: "faster-whisper"
    device: "auto"
```
Recommended options:

- **CUDA**: [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- **Metal/mps**: [`mlx-community/whisper-small-mlx`](https://huggingface.co/mlx-community/whisper-small-mlx)

---

#### Lightweight Local LLM (Shallow Analysis)

Used for fast, token-efficient entity detection, claim spotting, and summarization.

```yaml
  shallow_LLM:
    repo: "mistralai/Mistral-7B-Instruct-v0.2" 
    name: null
    adapter: "Mistral-7B-Instruct-v0_2_lora"
    adapter_type: "lora"
```

Recommended options:
- **CUDA**: [`mistralai/Mistral-7B-Instruct-v0.2`](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- **Metal/mps**: [`TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF`](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
- LoRA Adapter (see Adapters)

> Tip: If you're going to spend compute, spend it here. This model has the strongest effect on real-time analysis quality.

---

#### Semantic Filter
Used to detect and dedupe already seen topics and claims (i.e., filter them out of deep LLM requests).
```yaml
model:
  semantic:
    repo: "sentence-transformers/all-MiniLM-L6-v2"
    name: "all-MiniLM-L6-v2"
    backend: "sentence-transformer"
    similarity_threshold: 0.80
    context_minutes: 30
    context_limit: 1000
```
Recommended options:

- **CUDA**: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)  
- **Metal/mps**: [`mlx-community/MiniLM-L6-v2-mlx`](https://huggingface.co/mlx-community/MiniLM-L6-v2-mlx)

---

#### Deep LLM

Used for deeper, context-aware tasks such as:

- Claim verification
- Summary generation
- Evidence expansion

The deep LLM enriches the transcript by taking flagged items—like names, places, or controversial claims—and researching them in context. It generates expanded explanations, verifies facts, and provides supporting details that help users better understand what was said and why it matters. This is especially useful for surfacing nuance, historical background, or external references relevant to the conversation.

> Note: Requires API keys


```yaml
model:
  deep_LLM:
    client: 'openai'
    name: "gpt-4o"
    deep_search_temp: 0.3
    temp: 0.2
    recentFlagSize: 10
```

Example providers:

- [OpenAI (ChatGPT, GPT-4)](https://platform.openai.com/account/api-keys)
- [Anthropic Claude](https://console.anthropic.com/account/keys)
- [xAI Grok](https://grok.x.ai/)

---

### Extending with New Clients

Rachel uses a **plugin-style client interface** for all model backends. This includes:

- Transcription
- Shallow LLM
- Deep LLM
- Semantic Filter

To add support for a new backend (e.g., a different inference server or GGUF runtime), just implement a new client class under `src/rachel/clients/{type}/your_client.py`. Then register it in `config.yaml` like so:

```yaml
models:
  [your_client]:
    repo: ""
    name: ""
    backend: ""
```