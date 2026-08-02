# M.I.K.E. — slovenský návod

[Kanonický český README](../../README.md). M.I.K.E. je lokálny open-source český
hlasový asistent pre Macy s Apple Silicon. Whisper prepisuje reč, lokálna Ollama
vytvára odpoveď a lokálny OmniVoice ju nahovorí. **Verzia 0.1.1 je alfa:
aplikácia, dashboard a hlasové povely sú po česky; tento súbor prekladá celý
návod, nie runtime.** Nepoužívajte ho na núdzové, zdravotné, právne ani iné
vysoko rizikové rozhodnutia.

<!-- mike-doc:install -->
## Inštalácia

Požiadavky: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama a asi
15–25 GB voľného miesta podľa modelov. Modely ani médiá nie sú súčasťou
repozitára. OmniVoice používa samostatné prostredie, aby nekolidoval s Whisperom.

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

Pre OpenAI Whisper/PyTorch fallback použite `.[voice,torch,overlay]`. Kód
OmniVoice je Apache-2.0, ale predvolený model je **CC-BY-NC a nie je určený na
komerčné použitie**. Stiahne sa pri prvom štarte služby a nie je v repozitári.

<!-- mike-doc:first-run -->
## Prvé spustenie

Spustite `.venv/bin/mike start` a potom `.venv/bin/mike status`. Prvý štart môže
stiahnuť modely. Dashboard je len na `http://127.0.0.1:8140/` a OmniVoice na
`http://127.0.0.1:8130/`. Pri kolízii portu alebo starého procesu M.I.K.E.
skončí s vysvetlením a staršiu inštaláciu nezastaví ani neodstráni.

<!-- mike-doc:permissions -->
## Oprávnenia macOS

Pri prvom použití povoľte Python/M.I.K.E. v **Systémové nastavenia → Súkromie
a bezpečnosť → Mikrofón**. Po zamietnutí povoľte prístup ručne a spustite
`mike restart`. Overlay nepotrebuje Accessibility ani Screen Recording a nie
sú potrebné administrátorské práva.

<!-- mike-doc:configuration -->
## Konfigurácia

Súbor je v `~/Library/Application Support/MIKE/config.toml`; adresáre majú režim
700 a dátové súbory 600. Ollama, dashboard aj OmniVoice musia zostať na
loopbacku. Hlavné polia sú `assistant.model`, `stt.backend`, `stt.model`,
`server.port`, `[features]` a:

```toml
[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0
```

Verejné premenné majú prefix `MIKE_*`; `MIKE_HOME` izoluje test. Verejný server
má iba voice-design režim, neprijíma referenčné audio a neklonuje hlas.
Voiceprint vytvorte len z vlastného hlasu alebo s výslovným súhlasom hovoriaceho.

<!-- mike-doc:controls -->
## Ovládanie

Lifecycle príkazy sú `mike install|start|stop|restart|status|doctor|uninstall`.
Asistenta oslovte „Majku“; „Majku, stop“ preruší frontu OmniVoice. Pamäť používa
české frázy „pamatuj si, že …“ a „zapomeň na …“. Research a terminál sú opt-in.
Terminál povoľuje iba vybrané read-only príkazy bez shellu, pipe, presmerovania
a zápisu.

<!-- mike-doc:privacy -->
## Súkromie

Bez telemetrie. Dashboard, databáza, Ollama, prepis, voiceprint a OmniVoice sú
lokálne. Surové audio sa predvolene neukladá. Dočasný syntetický WAV má režim
600 a po `afplay` sa zmaže; server neprijíma referenčný hlas. Zapnutý research
odošle výslovnú otázku vyhľadávaču a vybraným verejným HTTPS webom. Pozrite
[PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Riešenie problémov

Začnite `mike doctor`. Pri Ollame skontrolujte `ollama list` a
`assistant.model`. Pri OmniVoice spustite `./scripts/omnivoice_service.sh status`,
pozrite `omnivoice-error.log` a `tts.omnivoice_url`. Bez prepisu skontrolujte
Mikrofón a `stt.device`. Ak je 8140 obsadený, zmeňte `server.port`. Starú
Whisper Flow/MAJKA zastavujte iba jej vlastným nástrojom.

<!-- mike-doc:uninstall -->
## Odinštalovanie

Spustite `.venv/bin/mike stop`, `.venv/bin/mike uninstall` a
`./scripts/omnivoice_service.sh uninstall`. Odstránia sa len LaunchAgenty
`io.github.emperorkundis.mike` a `io.github.emperorkundis.mike.omnivoice`;
dáta zostanú na obnovu. Po kontrole zálohy môžete presunúť
`~/Library/Application Support/MIKE` do Koša. Staršie inštalácie sa nezmenia.

<!-- mike-doc:warning -->
## Obmedzenia a licencie

v0.1.1 podporuje iba Apple Silicon macOS a český runtime. Prepis a odpoveď môžu
byť chybné; dôležité rozhodnutia musí kontrolovať človek. Zdroj M.I.K.E. je MIT,
atribúcie sú v [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Predvolený
OmniVoice model je CC-BY-NC a nie je na komerčné použitie. Zakázané sú
neoprávnené napodobňovanie hlasu, vydávanie sa za inú osobu a podvod. Bez binárok
a bez PyPI publikácie.
