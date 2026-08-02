# M.I.K.E. — deutsche Anleitung

[Kanonische tschechische README](../../README.md). M.I.K.E. ist ein lokaler,
quelloffener tschechischer Sprachassistent für Apple-Silicon-Macs. Whisper
transkribiert Sprache, lokales Ollama erzeugt die Antwort und lokales OmniVoice
spricht sie. **Version 0.1.1 ist Alpha: Anwendung, Dashboard und Sprachbefehle
sind tschechisch; diese Datei übersetzt die vollständige Anleitung, nicht die
Oberfläche.** Nicht für Notfälle, medizinische, rechtliche oder andere
Hochrisikoentscheidungen verwenden.

<!-- mike-doc:install -->
## Installation

Voraussetzungen: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama
und je nach Modellen etwa 15–25 GB freier Speicher. Modelle und Medien sind
nicht im Repository enthalten. OmniVoice läuft in einer separaten Umgebung,
damit es nicht mit Whisper kollidiert.

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

Für OpenAI Whisper/PyTorch stattdessen `.[voice,torch,overlay]` verwenden. Der
OmniVoice-Code steht unter Apache-2.0; das Standardmodell steht jedoch unter
**CC-BY-NC und ist nicht für kommerzielle Nutzung bestimmt**. Es wird beim
ersten Dienststart heruntergeladen und ist nicht Teil des Repositorys.

<!-- mike-doc:first-run -->
## Erster Start

`.venv/bin/mike start` und danach `.venv/bin/mike status` ausführen. Beim ersten
Start können Modelle heruntergeladen werden. Das Dashboard ist nur unter
`http://127.0.0.1:8140/`, OmniVoice nur unter `http://127.0.0.1:8130/`
erreichbar. Bei einem Port- oder Prozesskonflikt beendet sich M.I.K.E. mit einer
Erklärung, ohne eine ältere Installation zu stoppen oder zu entfernen.

<!-- mike-doc:permissions -->
## macOS-Berechtigungen

Beim ersten Gebrauch Python/M.I.K.E. unter **Systemeinstellungen → Datenschutz
& Sicherheit → Mikrofon** erlauben. Nach einer Ablehnung den Zugriff manuell
aktivieren und `mike restart` ausführen. Das Overlay benötigt weder
Bedienungshilfen noch Bildschirmaufnahme; Administratorrechte sind unnötig.

<!-- mike-doc:configuration -->
## Konfiguration

Die Datei liegt unter `~/Library/Application Support/MIKE/config.toml`;
Verzeichnisse haben Modus 700, Datendateien 600. Ollama, Dashboard und
OmniVoice müssen am Loopback gebunden bleiben. Wichtig sind `assistant.model`,
`stt.backend`, `stt.model`, `server.port`, `[features]` und:

```toml
[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0
```

Öffentliche Variablen tragen das Präfix `MIKE_*`; `MIKE_HOME` isoliert Tests.
Der öffentliche Server bietet nur Voice Design, nimmt kein Referenzaudio an
und klont keine Stimmen. Einen Voiceprint nur von der eigenen Stimme oder mit
ausdrücklicher Zustimmung der sprechenden Person erstellen.

<!-- mike-doc:controls -->
## Bedienung

Lebenszyklusbefehle: `mike install|start|stop|restart|status|doctor|uninstall`.
Den Assistenten mit „Majku“ ansprechen; „Majku, stop“ leert die OmniVoice-Warteschlange.
Der Speicher nutzt die tschechischen Sätze „pamatuj si, že …“ und „zapomeň na …“.
Recherche und Terminal sind Opt-in. Das Terminal erlaubt nur ausgewählte
Nur-Lese-Befehle ohne Shell, Pipes, Umleitungen oder Schreibzugriff.

<!-- mike-doc:privacy -->
## Datenschutz

Keine Telemetrie. Dashboard, Datenbank, Ollama, Transkription, Voiceprint und
OmniVoice bleiben lokal. Rohes Audio wird standardmäßig nicht gespeichert. Die
temporäre synthetische WAV-Datei hat Modus 600, wird nach `afplay` gelöscht und
der Server nimmt keine Referenzstimme an. Aktivierte Recherche sendet eine
ausdrückliche Anfrage an eine Suchmaschine und ausgewählte öffentliche
HTTPS-Seiten. Siehe [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Fehlerbehebung

Mit `mike doctor` beginnen. Für Ollama `ollama list` und `assistant.model`
prüfen. Für OmniVoice `./scripts/omnivoice_service.sh status` ausführen und
`omnivoice-error.log` sowie `tts.omnivoice_url` prüfen. Ohne Transkription die
Mikrofonberechtigung und `stt.device` prüfen. Bei belegtem Port 8140
`server.port` ändern. Eine alte Whisper-Flow/MAJKA-Installation nur mit deren
eigenem Werkzeug stoppen.

<!-- mike-doc:uninstall -->
## Deinstallation

`.venv/bin/mike stop`, `.venv/bin/mike uninstall` und
`./scripts/omnivoice_service.sh uninstall` ausführen. Entfernt werden nur die
LaunchAgents `io.github.emperorkundis.mike` und
`io.github.emperorkundis.mike.omnivoice`; Daten bleiben wiederherstellbar. Nach
Prüfung der Sicherung kann `~/Library/Application Support/MIKE` in den Papierkorb.
Ältere Installationen bleiben unverändert.

<!-- mike-doc:warning -->
## Einschränkungen und Lizenzen

v0.1.1 unterstützt nur Apple-Silicon-macOS und eine tschechische Laufzeit.
Transkripte und Antworten können falsch sein; wichtige Handlungen brauchen
menschliche Kontrolle. M.I.K.E.-Code ist MIT-lizenziert, Hinweise Dritter stehen
in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Das Standardmodell
von OmniVoice ist CC-BY-NC und nicht kommerziell nutzbar. Unbefugte
Stimmnachahmung, Identitätstäuschung und Betrug sind verboten. Keine Binärdateien
und keine PyPI-Veröffentlichung.
