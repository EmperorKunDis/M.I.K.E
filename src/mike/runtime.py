"""Jednoprocesový runtime: mikrofon, asistent, OmniVoice, dashboard a overlay."""

from __future__ import annotations

import asyncio
import fcntl
import logging
import os
import queue
import signal
import threading
import time
import wave
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

import uvicorn

from .assistant import Assistant
from .audio import BargeDetector, UtteranceSegmenter, capture_audio
from .config import Config
from .dashboard import create_app
from .database import Database
from .ollama import OllamaClient
from .overlay import NativeOverlay, OverlayState
from .paths import secure_file
from .research import ResearchClient
from .selfimprove import Judge, SafeTuner
from .stt import load_backend, pcm_to_float32
from .terminal import ReadOnlyTerminal
from .text_filters import filter_segments
from .tts import OmniVoiceTTS
from .voiceprint import VoiceprintGate

LOG = logging.getLogger(__name__)


class MikeRuntime:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.config.paths.ensure()
        self.database = Database(config.paths.database)
        self.database.initialize()
        self.ollama = OllamaClient(config.assistant.ollama_url, config.assistant.model)
        self.tts = OmniVoiceTTS(
            config.tts.omnivoice_url,
            enabled=config.tts.enabled,
        )
        self.assistant = Assistant(
            config,
            self.database,
            self.ollama,
            self.tts,
            research=ResearchClient(enabled=config.features.research),
            terminal=ReadOnlyTerminal(
                config.features.terminal_roots,
                enabled=config.features.terminal,
            ),
            judge=Judge(self.ollama) if config.features.self_improve else None,
        )
        self.overlay = OverlayState()
        self.stop_event = threading.Event()
        self._server: uvicorn.Server | None = None
        self._threads: list[threading.Thread] = []
        self._lock_handle: BinaryIO | None = None

    def acquire_lock(self) -> None:
        handle = self.config.paths.lock.open("a+b")
        secure_file(self.config.paths.lock)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            handle.close()
            raise RuntimeError("Jiný proces M.I.K.E. už drží aplikační zámek.") from exc
        self._lock_handle = handle
        self.config.paths.pid.write_text(f"{os.getpid()}\n", encoding="ascii")
        secure_file(self.config.paths.pid)

    def _dashboard(self) -> None:
        app = create_app(self.config, self.database, self.assistant)
        self._server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=self.config.server.host,
                port=self.config.server.port,
                log_level="warning",
                access_log=False,
            )
        )
        self._server.run()
        if not self.stop_event.is_set():
            LOG.error("Dashboard se neočekávaně zastavil.")
            self.stop_event.set()

    def _save_audio(self, pcm: bytes) -> Path:
        directory = self.config.paths.data / "audio"
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        path = directory / f"utterance-{stamp}.wav"
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16_000)
            output.writeframes(pcm)
        secure_file(path)
        return path

    async def _microphone_loop(self) -> None:
        chunks: queue.Queue[bytes] = queue.Queue(maxsize=64)
        stop = asyncio.Event()
        backend = await asyncio.to_thread(
            load_backend,
            self.config.stt.backend,
            self.config.stt.model,
            self.config.stt.language,
            self.config.paths,
        )
        segmenter = UtteranceSegmenter(
            silence_ms=self.config.stt.silence_ms,
            max_utterance_ms=self.config.stt.max_utterance_ms,
        )
        barge = BargeDetector()
        gate = VoiceprintGate(self.config.paths.voiceprint) if self.config.features.voiceprint else None
        capture = asyncio.create_task(capture_audio(chunks, stop, device=self.config.stt.device))
        self.overlay.update(status=f"Naslouchám · Whisper {backend.name}")
        try:
            while not self.stop_event.is_set():
                try:
                    data = await asyncio.to_thread(chunks.get, True, 0.2)
                except queue.Empty:
                    continue
                if self.tts.is_speaking:
                    if self.config.features.barge_in and barge.feed(
                        data, approve=(lambda chunk: gate.accepts_pcm(chunk)) if gate else None
                    ):
                        self.tts.stop()
                    continue
                barge.reset()
                utterance = segmenter.feed(data)
                if not utterance:
                    continue
                if gate and not gate.accepts_pcm(utterance):
                    LOG.info("Hlasový otisk odmítl neznámého mluvčího.")
                    continue
                if self.config.privacy.save_raw_audio:
                    self._save_audio(utterance)
                result = await asyncio.to_thread(backend.transcribe, pcm_to_float32(utterance))
                text, stats = filter_segments(result)
                LOG.debug("STT filter: %s", stats)
                if not text:
                    continue
                self.overlay.update(status="Přemýšlím", transcript=f"Uživatel: {text}", reply="")
                answer = await asyncio.to_thread(self.assistant.handle, text)
                self.overlay.update(
                    status="Mluvím" if answer.spoke else "Připraven",
                    reply=f"M.I.K.E.: {answer.reply}" if answer.reply else "",
                )
        finally:
            stop.set()
            await capture

    def _microphone(self) -> None:
        try:
            asyncio.run(self._microphone_loop())
        except Exception:
            LOG.exception("Mikrofonní/STT část selhala.")
            self.stop_event.set()

    def _tuner(self) -> None:
        tuner = SafeTuner(self.database)
        while not self.stop_event.wait(3600):
            try:
                tuner.propose_if_needed()
            except Exception:
                LOG.exception("Bezpečný tuner selhal; runtime pokračuje beze změny promptu.")

    def _start_thread(self, target, name: str) -> None:
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        self._threads.append(thread)

    def request_stop(self, *_args) -> None:
        self.stop_event.set()
        self.tts.stop()
        if self._server is not None:
            self._server.should_exit = True

    def run(self) -> None:
        self.acquire_lock()
        for current_signal in (signal.SIGINT, signal.SIGTERM):
            signal.signal(current_signal, self.request_stop)
        self._start_thread(self._dashboard, "mike-dashboard")
        if self.config.stt.enabled:
            self._start_thread(self._microphone, "mike-microphone")
        if self.config.features.self_improve:
            self._start_thread(self._tuner, "mike-tuner")
        try:
            no_overlay = os.environ.get("MIKE_NO_OVERLAY") == "1"
            if not no_overlay and NativeOverlay.available():
                NativeOverlay(self.overlay).run(self.stop_event)
            else:
                while not self.stop_event.wait(0.25):
                    pass
        finally:
            self.request_stop()
            for thread in self._threads:
                thread.join(timeout=8)
            self.config.paths.pid.unlink(missing_ok=True)
            if self._lock_handle is not None:
                self._lock_handle.close()
            time.sleep(0.05)
