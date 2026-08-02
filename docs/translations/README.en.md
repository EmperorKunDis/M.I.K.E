# M.I.K.E. — English guide

[Canonical Czech README](../../README.md). M.I.K.E. is a local open-source Czech
voice assistant for Apple Silicon Macs. Whisper transcribes speech, a local
Ollama model answers, and local OmniVoice provides speech. **Version 0.1.1 is alpha:
the application, dashboard, and voice commands are in Czech; this is a complete
translation of the guide, not of the runtime.** Do not use it for emergency,
medical, legal, or other high-risk decisions.

<!-- mike-doc:install -->
## Installation

Requirements: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama, and
roughly 10–20 GB of free space depending on your models. No model or media file
is bundled.

```bash
git clone https://github.com/EmperorKunDis/M.I.K.E.git
cd M.I.K.E
brew install python@3.12 portaudio ollama
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e ".[voice,mlx,overlay]"
ollama pull gemma3:12b
.venv/bin/mike install

python3.12 -m venv .venv-omnivoice
.venv-omnivoice/bin/python -m pip install --upgrade pip
.venv-omnivoice/bin/pip install -e ".[omnivoice]"
./scripts/omnivoice_service.sh install

.venv/bin/mike doctor
```

Use `.[voice,torch,overlay]` for the OpenAI Whisper/PyTorch fallback. Whisper,
Ollama, and each model have separate licenses and terms that you must review.
OmniVoice runs in the separate `.venv-omnivoice`; its code is Apache-2.0, but
the default model is **CC-BY-NC and not for commercial use**. It downloads on
the service's first start and is never bundled here.

<!-- mike-doc:first-run -->
## First run

Run `.venv/bin/mike start`, then `.venv/bin/mike status`. The first Whisper
startup may download a model. The dashboard is available only at
`http://127.0.0.1:8140/`. If a port or legacy process collides, M.I.K.E. stops
with an explanation; it never terminates or removes that older installation.

<!-- mike-doc:permissions -->
## macOS permissions

On first use, allow Python/M.I.K.E. under **System Settings → Privacy & Security
→ Microphone**. If access was denied, enable it there and run `mike restart`.
The overlay needs neither Accessibility nor Screen Recording. Administrator
rights are not required.

<!-- mike-doc:configuration -->
## Configuration

The canonical file is
`~/Library/Application Support/MIKE/config.toml`; directories use mode 700 and
data files mode 600. The default Ollama and dashboard addresses are loopback.
Research, terminal, voiceprint, telemetry, and raw-audio storage are off (the
last two must remain off unless the documented setting explicitly changes raw
audio). Main fields are `assistant.model`, `stt.backend`, `stt.model`,
`stt.device`, `server.port`, and `[features]`. Public environment overrides use
only `MIKE_*`; `MIKE_HOME` is useful for isolated testing.

OmniVoice uses `tts.omnivoice_url = "http://127.0.0.1:8130"`; `tts.model`,
`tts.instruct`, `tts.num_steps`, and `tts.speed` control voice design. The
public server accepts no reference audio and provides no voice-cloning mode.

To enable voiceprint recognition, first create a local embedding with
`python -m mike.voiceprint /path/to/your-own-voice.wav`, then set
`features.voiceprint = true`. Use only your own voice or a recording with the
speaker's explicit consent.

<!-- mike-doc:controls -->
## Controls

Lifecycle commands are `mike install|start|stop|restart|status|doctor|uninstall`.
Address the assistant as “Majku”. “Majku, stop” interrupts current speech.
Explicit memory uses Czech phrases equivalent to “remember that X is Y” and
“forget X”. Research runs only when enabled and explicitly requested with
“ověř na internetu …”. The terminal also requires an allowed root and the
Czech phrase “v terminálu spusť …”. It accepts only allowlisted read-only
commands, without a shell, pipes, redirects, or write operations.

<!-- mike-doc:privacy -->
## Privacy

There is no telemetry. Dashboard, database, Ollama, transcription, and the
voiceprint are local. Raw audio is not stored by default; transcripts, replies,
explicit memory, and ratings are stored in a private SQLite database. Enabling
research sends the explicit query to a search provider and selected public
HTTPS sites. See [PRIVACY.md](../../PRIVACY.md) for retention and deletion.
OmniVoice creates a mode-600 synthetic WAV only for playback and deletes it
after `afplay`; the public server accepts no reference voice.

<!-- mike-doc:troubleshooting -->
## Troubleshooting

Run `mike doctor` first. If Ollama fails, start it, check `ollama list`, and
match `assistant.model`. If there is no transcript, verify Microphone permission
and `stt.device`; an empty device selects the system default. Change
`server.port` if 8140 is busy. Stop an older Whisper Flow/MAJKA installation
with its own tool. Logs are under `~/Library/Application Support/MIKE/logs/`;
remove transcripts and personal data before sharing them.
If OmniVoice fails, run `./scripts/omnivoice_service.sh status`, inspect
`omnivoice-error.log`, and verify `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## Uninstallation

Run `.venv/bin/mike stop` and `.venv/bin/mike uninstall`. This removes only the
LaunchAgent `io.github.emperorkundis.mike` and preserves data for recovery. To
delete data, move `~/Library/Application Support/MIKE` to Trash after checking
your backup. Legacy installations remain untouched.
Run `./scripts/omnivoice_service.sh uninstall` to remove only the separate
`io.github.emperorkundis.mike.omnivoice` LaunchAgent.

<!-- mike-doc:warning -->
## Limitations and licenses

v0.1.1 supports only Apple Silicon macOS and a Czech runtime. Transcriptions and
answers may be wrong, and a human must supervise any consequential decision.
The source is MIT-licensed; inherited attribution is in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Models, dependencies,
and web sources keep their own licenses. No binaries or PyPI package are
published for v0.1.1. The default OmniVoice model is CC-BY-NC and not for
commercial use; never use it for unauthorized impersonation or fraud.
