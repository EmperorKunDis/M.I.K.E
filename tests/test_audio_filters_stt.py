from __future__ import annotations

from array import array

import pytest

from mike.audio import BargeDetector, UtteranceSegmenter, peak_int16, rms_int16
from mike.stt import bundled_model_files, decode_options, vocabulary_prompt
from mike.text_filters import DEFAULT_BLACKLIST, filter_segments, is_hallucination


def pcm(value: int, count: int = 1024) -> bytes:
    return array("h", [value] * count).tobytes()


def test_rms_empty_is_zero():
    assert rms_int16(b"") == 0


@pytest.mark.parametrize("value", [1, 50, 500, 1200, 32000])
def test_rms_constant_signal(value):
    assert rms_int16(pcm(value)) == pytest.approx(value)


def test_peak_uses_absolute_value():
    assert peak_int16(array("h", [-5, 2, 9]).tobytes()) == 9


def test_segmenter_waits_for_voice():
    segmenter = UtteranceSegmenter(threshold=500)
    assert segmenter.feed(pcm(20)) is None


def test_segmenter_keeps_preroll_and_finishes_after_silence():
    segmenter = UtteranceSegmenter(threshold=500, silence_ms=100)
    segmenter.feed(pcm(20))
    segmenter.feed(pcm(1000))
    result = None
    for _ in range(3):
        result = segmenter.feed(pcm(0)) or result
    assert result is not None
    assert len(result) >= len(pcm(1000))


def test_segmenter_hard_cap():
    segmenter = UtteranceSegmenter(threshold=1, max_utterance_ms=130)
    assert segmenter.feed(pcm(1000)) is None
    assert segmenter.feed(pcm(1000)) is None
    result = segmenter.feed(pcm(1000))
    assert result is not None


def test_segmenter_flush():
    segmenter = UtteranceSegmenter(threshold=1)
    segmenter.feed(pcm(1000))
    assert segmenter.flush()
    assert segmenter.flush() is None


def test_barge_calibrates_then_fires():
    detector = BargeDetector(floor=100, factor=2, sustain_chunks=2)
    for _ in range(8):
        assert not detector.feed(pcm(50))
    assert not detector.feed(pcm(500))
    assert detector.feed(pcm(500))
    assert not detector.feed(pcm(500))


def test_barge_gate_can_reject():
    detector = BargeDetector(floor=100, factor=2, sustain_chunks=1)
    for _ in range(8):
        detector.feed(pcm(50))
    assert not detector.feed(pcm(500), approve=lambda _data: False)


def test_barge_reset_allows_another_detection():
    detector = BargeDetector(floor=100, factor=2, sustain_chunks=1)
    for _ in range(8):
        detector.feed(pcm(50))
    assert detector.feed(pcm(500))
    detector.reset()
    assert not detector.fired


@pytest.mark.parametrize("text", DEFAULT_BLACKLIST)
def test_default_blacklist_is_filtered(text):
    assert is_hallucination(text)


@pytest.mark.parametrize("text", ["♪ hudba", "[potlesk]", "(hudba)", "...", "", "🎵 la la"])
def test_non_speech_markers_are_filtered(text):
    assert is_hallucination(text)


@pytest.mark.parametrize("text", ["Dnes je jasno.", "Jak funguje Ollama?", "M.I.K.E. poslouchá."])
def test_normal_czech_text_passes(text):
    assert not is_hallucination(text)


def test_filter_segments_keeps_quality_text():
    result = {
        "segments": [
            {"text": "Ahoj", "no_speech_prob": 0.1, "avg_logprob": -0.2, "compression_ratio": 1.1},
            {"text": "světe", "no_speech_prob": 0.1, "avg_logprob": -0.2, "compression_ratio": 1.1},
        ]
    }
    text, stats = filter_segments(result)
    assert text == "Ahoj světe"
    assert stats["segments"] == 2


@pytest.mark.parametrize(
    "segment",
    [
        {"text": "text", "no_speech_prob": 0.9},
        {"text": "text", "avg_logprob": -2},
        {"text": "text", "compression_ratio": 3},
    ],
)
def test_filter_segments_drops_low_quality(segment):
    text, stats = filter_segments({"segments": [segment]})
    assert text == ""
    assert stats["dropped_quality"] == 1


def test_filter_uses_top_level_text_fallback():
    text, _stats = filter_segments({"text": "Čistý přepis"})
    assert text == "Čistý přepis"


def test_vocabulary_prompt_is_bounded(app_paths):
    app_paths.ensure()
    (app_paths.data / "vocabulary.txt").write_text("jedna\ndvě\n" + "x" * 300, encoding="utf-8")
    prompt = vocabulary_prompt(app_paths, 20)
    assert prompt == "jedna, dvě"


def test_vocabulary_comments_are_ignored(app_paths):
    app_paths.ensure()
    (app_paths.data / "vocabulary.txt").write_text("# komentář\npojem\n", encoding="utf-8")
    assert vocabulary_prompt(app_paths) == "pojem"


@pytest.mark.parametrize("fp16", [True, False])
def test_decode_options_include_language(app_paths, fp16):
    options = decode_options("cs", app_paths, fp16=fp16)
    assert options["language"] == "cs"
    assert options["fp16"] is fp16


@pytest.mark.parametrize("suffix", [".pt", ".pth", ".onnx", ".safetensors", ".gguf"])
def test_bundled_model_scanner_finds_weights(tmp_path, suffix):
    path = tmp_path / f"model{suffix}"
    path.write_bytes(b"x")
    assert path in bundled_model_files(tmp_path)


def test_bundled_model_scanner_ignores_source(tmp_path):
    (tmp_path / "module.py").write_text("x = 1", encoding="utf-8")
    assert bundled_model_files(tmp_path) == []
