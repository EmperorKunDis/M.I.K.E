"""Volitelný nativní průhledný macOS overlay."""

from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class OverlaySnapshot:
    status: str = "Připraven"
    transcript: str = ""
    reply: str = ""


class OverlayState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._snapshot = OverlaySnapshot()

    def update(self, *, status: str | None = None, transcript: str | None = None, reply: str | None = None) -> None:
        with self._lock:
            current = self._snapshot
            self._snapshot = OverlaySnapshot(
                status=current.status if status is None else status,
                transcript=current.transcript if transcript is None else transcript,
                reply=current.reply if reply is None else reply,
            )

    def snapshot(self) -> OverlaySnapshot:
        with self._lock:
            return self._snapshot


class NativeOverlay:
    """AppKit okno; importuje PyObjC až při skutečném spuštění."""

    def __init__(self, state: OverlayState) -> None:
        self.state = state

    @staticmethod
    def available() -> bool:
        try:
            import AppKit  # noqa: F401
        except ImportError:
            return False
        return True

    def run(self, stop: threading.Event) -> None:  # pragma: no cover - nativní GUI
        from AppKit import (
            NSApplication,
            NSBackingStoreBuffered,
            NSColor,
            NSFloatingWindowLevel,
            NSMakeRect,
            NSTextField,
            NSWindow,
            NSWindowStyleMaskBorderless,
        )
        from Foundation import NSTimer

        app = NSApplication.sharedApplication()
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(30, 80, 520, 150), NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        window.setLevel_(NSFloatingWindowLevel)
        window.setOpaque_(False)
        window.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.03, 0.05, 0.09, 0.88))
        window.setHasShadow_(True)
        label = NSTextField.labelWithString_("")
        label.setFrame_(NSMakeRect(20, 18, 480, 114))
        label.setTextColor_(NSColor.whiteColor())
        label.setLineBreakMode_(0)
        label.setMaximumNumberOfLines_(5)
        window.contentView().addSubview_(label)
        window.orderFrontRegardless()

        def tick(_timer):
            snapshot = self.state.snapshot()
            label.setStringValue_(f"{snapshot.status}\n{snapshot.transcript}\n{snapshot.reply}".strip())
            if stop.is_set():
                app.terminate_(None)

        timer = NSTimer.scheduledTimerWithTimeInterval_repeats_block_(0.2, True, tick)
        app.run()
        timer.invalidate()
