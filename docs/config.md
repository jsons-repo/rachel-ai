# `config.yaml` Reference

[Installation](install.md)

[Configure LAN setup](lan_setup.md)

[Getting Started](getting_started.md)

[How It Works](how_it_works.md)

[config.yaml Reference](docs/config.md)

The `config.yaml` file controls how the app runs—everything from audio and networking to which models are loaded and how context is managed. Below is a breakdown of each section:

---

### `network`

Controls how the frontend (React) and backend (FastAPI) communicate.

| Key            | Description                                             |
|----------------|---------------------------------------------------------|
| `fe.host`      | Frontend host address (usually `"localhost"`).         |
| `fe.port`      | Frontend port. Default is `6677`.                       |
| `fe.protocol`  | Frontend protocol. Usually `"http"`.                    |
| `be.host`      | Backend host address (usually `"localhost"`).          |
| `be.port`      | Backend port. Default is `7766`.                        |
| `be.protocol`  | Backend protocol. Usually `"http"`.                     |

---

### `training`

Used when running batch processing or GPT-4-powered training pipelines.

| Key              | Description                                            |
|------------------|--------------------------------------------------------|
| `gpt_batch_size` | Number of transcript segments to process in one batch. |

---

### `audio`

Controls how audio is captured and chunked for processing.

| Key                 | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `chunk`             | Number of frames per audio chunk.                                           |
| `channels`          | Number of audio channels (`1` for mono).                                    |
| `rate`              | Sample rate in Hz (e.g. `16000` for Whisper).                               |
| `chunk_duration`    | Duration (in seconds) of each audio chunk.                                  |
| `overlap_duration`  | Overlap (in seconds) between chunks. Helps avoid word cut-off.              |
| `silence_threshold` | Amplitude threshold for silence detection. Lower = more sensitive.          |

---

### `model.transcription`

Controls the transcription backend (usually a Whisper variant).

| Key             | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `repo`           | Hugging Face model repo to download if not local.                          |
| `name`           | Local filename (optional, for GGUF-style backends).                        |
| `backend`        | Backend to use (`faster-whisper`, `whispercpp`, `mlx-whisper`).            |
| `device`         | Device for inference (`cuda`, `cpu`, `auto`, or `metal`).                  |
| `compute_type`   | Precision setting (`float16`, `float32`, `auto`, etc.).                    |
| `word_timestamps`| Whether to include word-level timing.                                      |
| `lang`           | Language code (e.g. `'en'`, `'es'`).                                        |
| `temp`           | Decoding temperature.                                                      |
| `beam_size`      | Beam search width. Higher = better results, slower speed.                  |
| `tolerance`      | Used when merging overlapping segments.                                    |

---

### `model.semantic`

Controls the semantic deduplication filter that blocks repeated claims.

| Key                  | Description                                                              |
|----------------------|---------------------------------------------------------------------------|
| `repo`               | Sentence-transformer model repo.                                          |
| `name`               | Local model name (usually same as repo).                                  |
| `backend`            | Backend used for inference (e.g. `"sentence-transformer"`).               |
| `similarity_threshold`| Cosine similarity threshold (e.g. `0.80`) for duplicate detection.       |
| `context_minutes`    | Time window (in minutes) to compare against for semantic duplicates.      |
| `context_limit`      | Maximum number of segments to hold in memory for comparison.              |

---

### `model.shallow_LLM`

Controls the fast, local LLM used for shallow analysis (entity detection and claim spotting).

| Key                  | Description                                                              |
|----------------------|---------------------------------------------------------------------------|
| `repo`               | Hugging Face model repo.                                                  |
| `name`               | Optional local filename (e.g. for GGUF models).                      
| `adapter`            | Optional LoRA adapter directory name.                                     |
| `adapter_type`       | Adapter type (e.g. `"lora"`).                                              |
| `backend`            | Backend to use (`hf-causal`, `gguf`, etc.).                               |
| `device`             | Execution device (`auto`, `cuda`, `cpu`, `metal`).                        |
| `compute_type`       | Precision (`auto`, `float16`, `int4`, etc.).                              |
| `do_sample`          | Whether to sample outputs (vs. greedy decoding).                          |
| `trust_remote_code`  | Whether to trust custom model code from Hugging Face.                     |
| `ctx_window_tokens`  | Number of input tokens allowed per prompt.                                |
| `max_tokens`         | Maximum output tokens to generate.                                        |
| `temperature`        | Sampling temperature.                                                     |
| `top_p`              | Nucleus sampling cutoff.                                                  |
| `top_k`              | Top-K filtering for sampling.                                             |
| `repetition_penalty` | Penalty for repeated phrases.                                             |
| `do_extra_pass`      | If true, runs an additional shallow pass (e.g. for summarization).        |

---

### `model.deep_LLM`

Controls the remote model used for high-quality, context-aware reasoning.

| Key                  | Description                                                              |
|----------------------|---------------------------------------------------------------------------|
| `name`           | Model name (e.g. `"gpt-4o"`, `"claude-3-opus"`).                           |
| `deep_search_temp`| Temperature for deep-search prompts (claim expansions, etc).               |
| `temp`           | Default temperature for summarization and general tasks.                   |
| `recentFlagSize` | Number of recent flagged segments to include in the deep model prompt.     |

---

### 📋 `summarization`

Controls how shallow and deep models receive context.

| Key                      | Description                                                             |
|--------------------------|-------------------------------------------------------------------------|
| `shallow_context_window` | Number of recent segments passed to the shallow model.                  |
| `deep_context_window`    | Number of recent segments passed to the deep model.                     |
| `silence_timeout`        | Seconds of silence before context resets.                               |