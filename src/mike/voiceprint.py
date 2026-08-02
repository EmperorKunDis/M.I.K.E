"""Opt-in rozpoznání hlasu pomocí lokálního embeddingu."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .paths import AppPaths, secure_file


class VoiceprintGate:
    def __init__(self, path: Path, threshold: float = 0.72) -> None:
        self.path = path
        self.threshold = threshold
        self._encoder = None
        self._reference = None

    def _dependencies(self):
        try:
            import numpy as np
            from resemblyzer import VoiceEncoder, preprocess_wav
        except ImportError as exc:
            raise RuntimeError("Rozpoznání hlasu vyžaduje sadu voice.") from exc
        if self._encoder is None:
            self._encoder = VoiceEncoder()
        return np, preprocess_wav

    def enroll_file(self, audio_file: Path) -> None:
        np, preprocess_wav = self._dependencies()
        waveform = preprocess_wav(audio_file)
        embedding = self._encoder.embed_utterance(waveform)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        np.save(self.path, embedding)
        secure_file(self.path)
        self._reference = embedding

    def available(self) -> bool:
        return self.path.exists()

    def accepts_pcm(self, pcm: bytes, sample_rate: int = 16_000) -> bool:
        np, _preprocess_wav = self._dependencies()
        if self._reference is None:
            if not self.path.exists():
                return False
            self._reference = np.load(self.path, allow_pickle=False)
        waveform = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        if sample_rate != 16_000:
            raise RuntimeError("Voiceprint očekává PCM 16 kHz.")
        candidate = self._encoder.embed_utterance(waveform)
        similarity = float(np.dot(self._reference, candidate))
        return similarity >= self.threshold


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m mike.voiceprint",
        description="Vytvoří lokální hlasový embedding z vlastní WAV nahrávky.",
    )
    parser.add_argument("audio_file", type=Path)
    args = parser.parse_args(argv)
    if not args.audio_file.is_file():
        parser.error("audio_file neexistuje nebo není soubor")
    paths = AppPaths.from_env()
    load_config(paths)
    gate = VoiceprintGate(paths.voiceprint)
    gate.enroll_file(args.audio_file)
    print(f"Voiceprint uložen lokálně: {paths.voiceprint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
