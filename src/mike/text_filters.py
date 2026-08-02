"""Filtry běžných Whisper halucinací a nekvalitních segmentů."""

from __future__ import annotations

MUSIC_MARKERS = ("♪", "♫", "🎵", "🎶", "🎼")
DEFAULT_BLACKLIST = (
    "titulky vytvořil",
    "titulky vytvořila",
    "překlad a titulky",
    "děkuji za zhlédnutí",
    "děkujeme za zhlédnutí",
    "díky za sledování",
    "děkuji za pozornost",
    "přihlaste se k odběru",
    "thank you for watching",
    "thanks for watching",
    "subtitles by",
)
NO_SPEECH_MAX = 0.6
COMPRESSION_MAX = 2.4
AVG_LOGPROB_MIN = -1.0


def is_hallucination(text: str, blacklist: tuple[str, ...] = DEFAULT_BLACKLIST) -> bool:
    stripped = text.strip()
    if not stripped or not any(character.isalnum() for character in stripped):
        return True
    if any(marker in stripped for marker in MUSIC_MARKERS):
        return True
    if (stripped.startswith("[") and stripped.endswith("]")) or (stripped.startswith("(") and stripped.endswith(")")):
        return True
    folded = stripped.casefold()
    return any(phrase.casefold() in folded for phrase in blacklist)


def filter_segments(
    result: dict,
    blacklist: tuple[str, ...] = DEFAULT_BLACKLIST,
) -> tuple[str, dict[str, int | float]]:
    """Vrátí spojený bezpečný přepis a anonymní statistiku filtru."""
    kept: list[str] = []
    stats: dict[str, int | float] = {
        "segments": 0,
        "dropped_quality": 0,
        "dropped_blacklist": 0,
        "max_no_speech_prob": 0.0,
        "min_avg_logprob": 0.0,
    }
    segments = result.get("segments") or []
    if not segments and result.get("text"):
        segments = [{"text": result["text"]}]
    for segment in segments:
        stats["segments"] = int(stats["segments"]) + 1
        no_speech = float(segment.get("no_speech_prob", 0.0))
        logprob = float(segment.get("avg_logprob", 0.0))
        compression = float(segment.get("compression_ratio", 0.0))
        stats["max_no_speech_prob"] = max(float(stats["max_no_speech_prob"]), no_speech)
        stats["min_avg_logprob"] = min(float(stats["min_avg_logprob"]), logprob)
        if no_speech >= NO_SPEECH_MAX or compression >= COMPRESSION_MAX or logprob < AVG_LOGPROB_MIN:
            stats["dropped_quality"] = int(stats["dropped_quality"]) + 1
            continue
        text = str(segment.get("text", "")).strip()
        if not text:
            continue
        if is_hallucination(text, blacklist):
            stats["dropped_blacklist"] = int(stats["dropped_blacklist"]) + 1
            continue
        kept.append(text)
    joined = " ".join(kept)
    if joined and is_hallucination(joined, blacklist):
        stats["dropped_blacklist"] = int(stats["dropped_blacklist"]) + 1
        joined = ""
    return joined, stats
