# M.I.K.E. — türkmençe gollanma

[Çeh dilindäki esasy README](../../README.md). M.I.K.E. Apple Silicon Mac üçin
ýerli, açyk çeşmeli çeh ses kömekçisidir. Whisper gepleşigi tekste geçirýär,
ýerli Ollama jogap berýär, macOS `say` bolsa ony okaýar. **0.1 alpha wersiýa:
programma, panel we ses buýruklary çeh dilindedir. Bu interfeýsiň däl, doly
gollanmanyň terjimesidir.** Gyssagly, lukmançylyk, hukuk ýa-da ýokary töwekgel
kararlar üçin ulanmaň.

<!-- mike-doc:install -->
## Gurmak

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama we modele görä
takmynan 10–20 GB gerek. Modeller we media repozitoriýada ýok.

```bash
git clone https://github.com/EmperorKunDis/M.I.K.E.git
cd M.I.K.E
brew install python@3.12 portaudio ollama
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e ".[voice,mlx,overlay]"
ollama pull gemma3:12b
.venv/bin/mike install
.venv/bin/mike doctor
```

OpenAI Whisper/PyTorch fallback üçin `.[voice,torch,overlay]` ulanyň. Whisper,
Ollama we her modeliň öz ygtyýarnamasy hem şertleri bar.

<!-- mike-doc:first-run -->
## Ilkinji başlangyç

`.venv/bin/mike start`, soň `.venv/bin/mike status` işlediň. Whisper ilkinji
gezek modeli ýükläp biler. Panel diňe `http://127.0.0.1:8140/` salgysynda.
Port ýa-da köne proses çaknyşsa, M.I.K.E. düşündiriş bilen durýar; köne gurnawy duruzmaýar ýa-da pozmaýar.

<!-- mike-doc:permissions -->
## macOS rugsatlary

**System Settings → Privacy & Security → Microphone** bölüminde Python/M.I.K.E.
rugsat beriň. Ret edilen bolsa, açyp `mike restart` işlediň. Overlay
Accessibility ýa-da Screen Recording talap etmeýär. Admin hukugy gerek däl.

<!-- mike-doc:configuration -->
## Sazlama

Faýl `~/Library/Application Support/MIKE/config.toml`; kataloglar 700, maglumat
faýllary 600 režimde. Ollama we dashboard loopback ulanýar. Research, terminal
we voiceprint öçük; telemetriýa ýok, raw audio saklanmaýar. Esasy meýdanlar:
`assistant.model`, `stt.backend`, `stt.model`, `stt.device`, `server.port`,
`[features]`. `MIKE_HOME` synagy aýyrýar; üýtgeýjiler `MIKE_*`.

Voiceprint-i ýerli dörediň:
`python -m mike.voiceprint /oz-sesinize/yol.wav`, soň
`features.voiceprint = true` ediň. Diňe öz sesiňizi ýa-da açyk razylygy ulanyň.

<!-- mike-doc:controls -->
## Dolandyryş

Buýruklar: `mike install|start|stop|restart|status|doctor|uninstall`. Kömekçä
çehçe “Majku” diýiň; “Majku, stop” geplemegi kesýär. Ýat: “pamatuj si, že X je
Y” we “zapomeň na X”. Research opt-in we “ověř na internetu …” talap edýär.
Read-only terminal rugsatly root we “v terminálu spusť …” talap edýär; shell,
pipe, redirect we ýazmak goldanylmaýar.

<!-- mike-doc:privacy -->
## Gizlinlik

Telemetriýa ýok. Dashboard, Ollama, baza, transkripsiýa we voiceprint ýerli.
Raw audio deslapky ýagdaýda saklanmaýar; hususy SQLite tekst, jogap, açyk ýat we
bahalary saklaýar. Açylan research diňe açyk soragy gözlege we saýlanan jemgyýetçilik
HTTPS sahypalaryna iberýär. [PRIVACY.md](../../PRIVACY.md) serediň.

<!-- mike-doc:troubleshooting -->
## Meseleleri çözmek

`mike doctor` bilen başlaň. Ollama-ny açyp `ollama list` we `assistant.model`
barlaň. Tekst ýok bolsa, Microphone we `stt.device` barlaň; boş baha ulgam
girişidir. 8140 meşgul bolsa, `server.port` üýtgediň. Köne Whisper Flow/MAJKA-ny
öz guraly bilen duruzyň. Loglar `~/Library/Application Support/MIKE/logs/` içinde;
paýlaşmazdan öň şahsy maglumatlary aýyryň.

<!-- mike-doc:uninstall -->
## Aýyrmak

`.venv/bin/mike stop` we `.venv/bin/mike uninstall` işlediň. Diňe LaunchAgent
`io.github.emperorkundis.mike` aýrylýar; maglumat dikeltmek üçin galýar. Doly
pozmak üçin backup-y barlap `~/Library/Application Support/MIKE` bukjasyny Trash-a
geçiriň. Köne gurnawlar üýtgemeýär.

<!-- mike-doc:warning -->
## Çäklendirmeler we ygtyýarnamalar

v0.1 diňe Apple Silicon macOS we çeh runtime goldaýar. Tekst we jogap ýalňyş
bolup biler; möhüm hereketi adam gözegçilik edýär. Kod MIT, atribusiýa
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Modeller,
baglylyklar we web çeşmeleriň öz ygtyýarnamasy bar; binary we PyPI ýok.
