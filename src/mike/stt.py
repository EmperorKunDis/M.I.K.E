"""Volitelné Whisper backendy; modely se nikdy nebalí do repozitáře."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from .paths import AppPaths

LOG = logging.getLogger(__name__)
MLX_MODELS = {
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "medium": "mlx-community/whisper-medium-mlx",
    "small": "mlx-community/whisper-small-mlx",
}


class Backend(Protocol):
    name: str

    def transcribe(self, audio: object) -> dict: ...


def vocabulary_prompt(paths: AppPaths, limit: int = 200) -> str | None:
    path = paths.data / "vocabulary.txt"
    try:
        terms = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except OSError:
        return None
    prompt = ""
    for term in terms:
        candidate = f"{prompt}, {term}" if prompt else term
        if len(candidate) > limit:
            break
        prompt = candidate
    return prompt or None


def decode_options(language: str, paths: AppPaths, *, fp16: bool) -> dict:
    options = {
        "language": language,
        "fp16": fp16,
        "temperature": (0.0, 0.2, 0.4),
        "condition_on_previous_text": False,
        "no_speech_threshold": 0.6,
        "logprob_threshold": -1.0,
        "compression_ratio_threshold": 2.4,
    }
    prompt = vocabulary_prompt(paths)
    if prompt:
        options["initial_prompt"] = prompt
    return options


class TorchBackend:
    name = "torch"

    def __init__(self, model: str, language: str, paths: AppPaths) -> None:
        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError("Chybí openai-whisper; nainstalujte sadu torch.") from exc
        self._model = whisper.load_model(model)
        self._options = decode_options(language, paths, fp16=False)

    def transcribe(self, audio: object) -> dict:
        return self._model.transcribe(audio, **self._options)


class MlxBackend:
    name = "mlx"

    def __init__(self, model: str, language: str, paths: AppPaths) -> None:
        try:
            import mlx_whisper
        except ImportError as exc:
            raise RuntimeError("Chybí mlx-whisper; nainstalujte sadu mlx.") from exc
        self.repo = model if "/" in model else MLX_MODELS.get(model, f"mlx-community/whisper-{model}-mlx")
        self._options = decode_options(language, paths, fp16=True)
        self._transcribe = mlx_whisper.transcribe

    def transcribe(self, audio: object) -> dict:
        return self._transcribe(audio, path_or_hf_repo=self.repo, **self._options)


def load_backend(name: str, model: str, language: str, paths: AppPaths) -> Backend:
    if name == "mlx":
        try:
            return MlxBackend(model, language, paths)
        except RuntimeError:
            LOG.warning("MLX backend není dostupný, zkouším torch.")
    return TorchBackend(model, language, paths)


def pcm_to_float32(data: bytes) -> object:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Pro STT chybí numpy; nainstalujte sadu voice.") from exc
    return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0


def bundled_model_files(repo: Path) -> list[Path]:
    """Pomocná auditní kontrola: v repozitáři nesmí být modelové váhy."""
    suffixes = {".pt", ".pth", ".onnx", ".safetensors", ".gguf"}
    return [path for path in repo.rglob("*") if path.is_file() and path.suffix.casefold() in suffixes]
