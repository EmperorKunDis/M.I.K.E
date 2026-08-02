# M.I.K.E. — ghid în limba română

[README canonic în cehă](../../README.md). M.I.K.E. este un asistent vocal ceh,
local și open-source, pentru Mac cu Apple Silicon. Whisper transcrie, modelul
local Ollama răspunde, iar OmniVoice local redă vocea. **Versiunea 0.1.1 este
alpha: aplicația, panoul și comenzile vocale sunt în cehă. Acesta este ghidul
complet tradus, nu interfața tradusă.** Nu folosiți aplicația pentru urgențe,
medicină, drept sau alte decizii cu risc ridicat.

<!-- mike-doc:install -->
## Instalare

Necesită macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama și circa
10–20 GB, în funcție de modele. Modelele și fișierele media nu sunt incluse.

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

Pentru fallback OpenAI Whisper/PyTorch instalați `.[voice,torch,overlay]`.
Whisper, Ollama și fiecare model au licențe și condiții proprii.
OmniVoice rulează în `.venv-omnivoice` separat; codul este Apache-2.0, însă
modelul implicit este **CC-BY-NC și nu poate fi folosit comercial**. Modelul se
descarcă la prima pornire a serviciului și nu este inclus în depozit.

<!-- mike-doc:first-run -->
## Prima pornire

Rulați `.venv/bin/mike start`, apoi `.venv/bin/mike status`. Prima pornire
Whisper poate descărca modelul. Panoul există numai la
`http://127.0.0.1:8140/`. La o coliziune de port sau proces vechi, M.I.K.E. se
oprește cu explicație; nu termină și nu șterge instalarea veche.

<!-- mike-doc:permissions -->
## Permisiuni macOS

Permiteți Python/M.I.K.E. în **System Settings → Privacy & Security →
Microphone**. Dacă accesul a fost refuzat, activați-l și rulați `mike restart`.
Overlay-ul nu cere Accessibility sau Screen Recording. Nu sunt necesare drepturi admin.

<!-- mike-doc:configuration -->
## Configurare

Fișierul este `~/Library/Application Support/MIKE/config.toml`; directoarele au
mod 700, fișierele de date 600. Ollama și dashboard-ul folosesc loopback.
Research, terminal și voiceprint sunt oprite; nu există telemetrie, iar audio
brut nu se salvează. Câmpuri principale: `assistant.model`, `stt.backend`,
`stt.model`, `stt.device`, `server.port`, `[features]`. `MIKE_HOME` izolează un
test; variabilele publice folosesc prefixul `MIKE_*`.

OmniVoice folosește `tts.omnivoice_url = "http://127.0.0.1:8130"`; câmpurile
`tts.model`, `tts.instruct`, `tts.num_steps` și `tts.speed` controlează designul
vocii. Serverul public nu acceptă audio de referință și nu clonează voci.

Creați voiceprint local cu
`python -m mike.voiceprint /cale/catre/vocea-proprie.wav`, apoi setați
`features.voiceprint = true`. Folosiți numai vocea proprie sau acordul explicit.

<!-- mike-doc:controls -->
## Control

Comenzi: `mike install|start|stop|restart|status|doctor|uninstall`. Adresați-vă
în cehă cu „Majku”; „Majku, stop” întrerupe vocea. Memoria folosește „pamatuj si,
že X je Y” și „zapomeň na X”. Research cere opt-in și „ověř na internetu …”.
Terminalul read-only cere o rădăcină permisă și „v terminálu spusť …”; shell,
pipe, redirecționări și operații de scriere nu sunt acceptate.

<!-- mike-doc:privacy -->
## Confidențialitate

Nu există telemetrie. Panoul, Ollama, baza, transcrierea și voiceprint-ul sunt
locale. Audio brut nu este stocat implicit; SQLite privată păstrează texte,
răspunsuri, memoria explicită și evaluări. Research activ trimite doar cererea
explicită unui motor de căutare și site-urilor HTTPS publice selectate. Vedeți
[PRIVACY.md](../../PRIVACY.md).
OmniVoice este local; WAV-ul sintetic temporar are modul 600 și este șters după
`afplay`, iar serverul nu acceptă o voce de referință.

<!-- mike-doc:troubleshooting -->
## Depanare

Începeți cu `mike doctor`. Pentru Ollama porniți serviciul, verificați
`ollama list` și `assistant.model`. Fără transcriere, verificați Microphone și
`stt.device`; gol înseamnă intrarea implicită. Schimbați `server.port` dacă
8140 este ocupat. Opriți vechiul Whisper Flow/MAJKA cu instrumentul propriu.
Logurile sunt în `~/Library/Application Support/MIKE/logs/`; eliminați datele
personale înainte de partajare.
Dacă OmniVoice nu răspunde, rulați `./scripts/omnivoice_service.sh status`,
verificați `omnivoice-error.log` și `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## Dezinstalare

Rulați `.venv/bin/mike stop` și `.venv/bin/mike uninstall`. Se elimină numai
LaunchAgent `io.github.emperorkundis.mike`; datele rămân pentru recuperare.
După verificarea copiei de siguranță, mutați
`~/Library/Application Support/MIKE` în Trash pentru ștergere totală. Instalările vechi rămân intacte.
`./scripts/omnivoice_service.sh uninstall` elimină doar LaunchAgent-ul separat
`io.github.emperorkundis.mike.omnivoice`.

<!-- mike-doc:warning -->
## Limitări și licențe

v0.1.1 suportă numai macOS Apple Silicon și runtime ceh. Transcrierile și
răspunsurile pot fi greșite; omul supraveghează orice acțiune importantă. Codul
este MIT, cu atribuiri în [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
Modelele, dependențele și sursele web au licențe proprii; nu există binare sau PyPI.
Modelul OmniVoice implicit este CC-BY-NC și nu permite utilizare comercială;
nu îl folosiți pentru imitare neautorizată sau fraudă.
