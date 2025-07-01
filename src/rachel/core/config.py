# src/rachel/core/config.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, TypeVar, Type, Annotated
from pathlib import Path
from dotenv import load_dotenv
import yaml
import os
from threading import Lock

# 📦 Local stuff
USER_ROOT = Path.home()
LOCAL_RACHEL_DIR = USER_ROOT / ".rachel"
T = TypeVar('T')
load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")

class ConfigError(Exception):
    """Raised when configuration is invalid"""
    pass

def env_var(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with optional default"""
    value = os.getenv(key, default)
    if value is None:
        raise ConfigError(f"Required environment variable {key} not set")
    return value

@dataclass
class NetworkConfig:
    host: str
    port: int
    protocol: str

@dataclass
class FullNetworkConfig:
    fe: NetworkConfig
    be: NetworkConfig

@dataclass
class TrainingConfig:
    gpt_batch_size: int

@dataclass
class AudioConfig:
    chunk: int
    channels: int
    rate: int
    chunk_duration: float
    overlap_duration: float
    silence_threshold: float

    def __post_init__(self):
        if self.rate <= 0:
            raise ConfigError(f"Audio rate must be positive, got {self.rate}")
        if self.chunk_duration <= 0:
            raise ConfigError(f"Chunk duration must be positive, got {self.chunk_duration}")
        
@dataclass
class SemanticFilterConfig:
    repo: str
    name: str  
    backend: str
    similarity_threshold: float
    context_minutes: int
    context_limit: int

    def __post_init__(self):
        if not (0.0 < self.similarity_threshold <= 1.0):
            raise ConfigError(f"similarity_threshold must be between 0 and 1, got {self.similarity_threshold}")
        if self.context_minutes <= 0:
            raise ConfigError(f"context_minutes must be positive, got {self.context_minutes}")
        if self.context_limit <= 0:
            raise ConfigError(f"context_limit must be positive, got {self.context_limit}")


@dataclass
class TranscriptionModelConfig:
    repo: str
    name: Optional[str] = None 
    backend: str = "faster-whisper"
    device: str = "auto"
    compute_type: str = "auto"
    word_timestamps: bool = True
    lang: str = 'en'
    temp: float = 0.3
    beam_size: int = 3
    tolerance: float = 0.1

    def __post_init__(self):
        if not self.repo:
            raise ConfigError("Transcription model 'repo' is required")
        if self.temp < 0 or self.temp > 1:
            raise ConfigError(f"Temperature must be between 0 and 1, got {self.temp}")

@dataclass
class ShallowLLMConfig:
    repo: str
    name: Optional[str] = None
    adapter: Optional[str] = None
    adapter_type: Optional[str] = None
    backend: str = "hf-causal"
    device: str = "auto"
    compute_type: str = "auto"
    do_sample: bool = False
    trust_remote_code: bool = True
    ctx_window_tokens: int = 2048
    max_tokens: int = 128
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.1
    do_extra_pass: bool = False

@dataclass
class DeepLLMConfig:
    client: str
    name: str
    deep_search_temp: float = 0.4
    temp: float = 0.3
    recentFlagSize: int = 10

@dataclass
class ModelConfig:
    transcription: TranscriptionModelConfig
    shallow_LLM: ShallowLLMConfig
    deep_LLM: DeepLLMConfig
    semantic: SemanticFilterConfig

@dataclass
class SummarizationConfig:
    shallow_context_window: int
    deep_context_window: int
    silence_timeout: float

@dataclass
class RachelConfig:
    network: FullNetworkConfig
    training: TrainingConfig
    audio: AudioConfig
    model: ModelConfig
    summarization: SummarizationConfig

    hf_token: Annotated[Optional[str], "env"] = field(default_factory=lambda: os.getenv("HF_TOKEN"))
    deep_api_key: Annotated[Optional[str], "env"] = field(default_factory=lambda: os.getenv("DEEP_API_KEY"))

    # Note: Adapters are meant to be checked in; so they don't store at .rachel/cache like HF
    adapter_root: str = field(default_factory=lambda: str(Path(__file__).resolve().parents[3] / "models"))

    # Note: These are models users download and store locally at .rachel
    shallow_root: str = field(default_factory=lambda: str(LOCAL_RACHEL_DIR / "models" / "shallow"))
    transcription_root: str = field(default_factory=lambda: str(LOCAL_RACHEL_DIR / "models" / "transcription"))
    embedded_filter_root: str = field(default_factory=lambda: str(LOCAL_RACHEL_DIR / "models" / "embedded_filter"))

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> 'RachelConfig':
        """Load config from YAML file with error handling"""
        if path is None:
            env_override = os.getenv("RACHEL_CONFIG")
            if env_override:
                path = Path(env_override)
            else:
                path = Path(__file__).resolve().parents[3] / "config.yaml"


        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {path}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to read config from {path}: {e}")

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'RachelConfig':
        """Internal method to create config from dict with validation"""
        try:
            return cls(
                network=FullNetworkConfig(
                    fe=NetworkConfig(**data['network']['fe']),
                    be=NetworkConfig(**data['network']['be'])
                ),
                training=TrainingConfig(**data.get('training', {})),
                audio=AudioConfig(**data['audio']),
                model=ModelConfig(
                    transcription=TranscriptionModelConfig(**data['model']['transcription']),
                    semantic=SemanticFilterConfig(**data['model']['semantic']),
                    shallow_LLM=ShallowLLMConfig(**data['model']['shallow_LLM']),
                    deep_LLM=DeepLLMConfig(**data['model']['deep_LLM'])
                ),
                summarization=SummarizationConfig(**data['summarization'])
            )
        except KeyError as e:
            raise ConfigError(f"Missing required config key: {e}")
        except TypeError as e:
            raise ConfigError(f"Invalid config structure: {e}")

_config: Optional[RachelConfig] = None
_config_lock = Lock()

def get_config() -> RachelConfig:
    """Get the global config instance (thread-safe)"""
    global _config
    if _config is None:
        with _config_lock:
            if _config is None:
                _config = RachelConfig.from_yaml()
    return _config

def set_config(cfg: RachelConfig) -> None:
    """Override global config (useful for testing)"""
    global _config
    with _config_lock:
        _config = cfg

def reset_config() -> None:
    """Reset config to force reload next time"""
    global _config
    with _config_lock:
        _config = None

def get_transcription_config() -> TranscriptionModelConfig:
    """Convenience method to get transcription config"""
    return get_config().model.transcription
