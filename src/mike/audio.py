"""Mikrofonní capture a skládání řečových úseků.

Capture smyčka vychází z MIT projektu Whisper Flow (Dima Statz); viz
``THIRD_PARTY_NOTICES.md``. Veřejná verze neukládá PCM, pokud to uživatel
výslovně nezapne v konfiguraci.
"""

from __future__ import annotations

import asyncio
import math
import queue
from array import array
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

SAMPLE_RATE = 16_000
CHUNK_SIZE = 1024


def rms_int16(data: bytes) -> float:
    samples = array("h")
    samples.frombytes(data)
    if not samples:
        return 0.0
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


def peak_int16(data: bytes) -> int:
    samples = array("h")
    samples.frombytes(data)
    return max((abs(sample) for sample in samples), default=0)


def find_input_device(audio: Any, wanted: str) -> int | None:
    """Najde vstupní zařízení podle části názvu; prázdné znamená systémový default."""
    if not wanted.strip():
        return None
    needle = wanted.casefold()
    for index in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(index)
        if int(info.get("maxInputChannels", 0)) > 0 and needle in str(info.get("name", "")).casefold():
            return index
    raise RuntimeError(f"Vstupní zařízení obsahující „{wanted}“ nebylo nalezeno.")


async def capture_audio(
    chunks: queue.Queue[bytes],
    stop: asyncio.Event,
    *,
    device: str = "",
    sample_rate: int = SAMPLE_RATE,
    chunk_size: int = CHUNK_SIZE,
) -> None:  # pragma: no cover - vyžaduje skutečný mikrofon
    """Čte nejnovější PCM bez blokování event loopu a toleruje overflow."""
    try:
        import pyaudio
    except ImportError as exc:
        raise RuntimeError("Chybí PyAudio; nainstalujte volitelnou sadu voice.") from exc
    loop = asyncio.get_running_loop()
    audio = pyaudio.PyAudio()
    device_index = find_input_device(audio, device)
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=chunk_size,
    )
    try:
        while not stop.is_set():
            data = await loop.run_in_executor(None, stream.read, chunk_size, False)
            try:
                chunks.put_nowait(data)
            except queue.Full:
                try:
                    chunks.get_nowait()
                except queue.Empty:
                    pass
                chunks.put_nowait(data)
            await asyncio.sleep(0)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


@dataclass
class UtteranceSegmenter:
    """Jednoduchá energy VAD s pre-roll a ukončením po tichu."""

    threshold: int = 500
    silence_ms: int = 650
    max_utterance_ms: int = 30_000
    sample_rate: int = SAMPLE_RATE
    chunk_size: int = CHUNK_SIZE

    def __post_init__(self) -> None:
        self._chunks: list[bytes] = []
        self._pre_roll: list[bytes] = []
        self._silent_chunks = 0
        self._speaking = False

    @property
    def chunk_ms(self) -> float:
        return self.chunk_size / self.sample_rate * 1000

    def feed(self, data: bytes) -> bytes | None:
        voiced = peak_int16(data) >= self.threshold
        if not self._speaking:
            self._pre_roll = (self._pre_roll + [data])[-3:]
            if not voiced:
                return None
            self._speaking = True
            self._chunks = list(self._pre_roll)
            self._silent_chunks = 0
            return None

        self._chunks.append(data)
        self._silent_chunks = 0 if voiced else self._silent_chunks + 1
        duration = len(self._chunks) * self.chunk_ms
        silent_for = self._silent_chunks * self.chunk_ms
        if silent_for >= self.silence_ms or duration >= self.max_utterance_ms:
            utterance = b"".join(self._chunks[: len(self._chunks) - self._silent_chunks or None])
            self.reset()
            return utterance
        return None

    def flush(self) -> bytes | None:
        if not self._chunks:
            return None
        utterance = b"".join(self._chunks)
        self.reset()
        return utterance

    def reset(self) -> None:
        self._chunks = []
        self._pre_roll = []
        self._silent_chunks = 0
        self._speaking = False


class BargeDetector:
    """Detekuje setrvalý hlas nad reproduktorovým bleedem."""

    def __init__(self, floor: float = 1200, factor: float = 3, sustain_chunks: int = 6) -> None:
        self.floor = floor
        self.factor = factor
        self.sustain_chunks = sustain_chunks
        self.bleed = 0.0
        self.seen = 0
        self.loud_run = 0
        self.fired = False

    def feed(self, data: bytes, approve: Callable[[bytes], bool] | None = None) -> bool:
        if self.fired:
            return False
        value = rms_int16(data)
        if self.seen < 8:
            self.bleed = value if self.seen == 0 else 0.7 * self.bleed + 0.3 * value
            self.seen += 1
            return False
        self.loud_run = self.loud_run + 1 if value > max(self.floor, self.factor * self.bleed) else 0
        if self.loud_run < self.sustain_chunks:
            return False
        if approve is not None and not approve(data):
            self.loud_run = 0
            return False
        self.fired = True
        return True

    def reset(self) -> None:
        self.bleed = 0.0
        self.seen = 0
        self.loud_run = 0
        self.fired = False
