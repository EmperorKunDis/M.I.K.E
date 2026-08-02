# M.I.K.E. — instrukcja po polsku

[Kanoniczny README po czesku](../../README.md). M.I.K.E. to lokalny,
open-source'owy czeski asystent głosowy dla komputerów Mac z Apple Silicon.
Whisper transkrybuje mowę, lokalna Ollama tworzy odpowiedź, a lokalny OmniVoice
ją odczytuje. **Wersja 0.1.1 jest alfa: aplikacja, panel i polecenia głosowe są
po czesku; ten plik tłumaczy pełną instrukcję, nie interfejs.** Nie używaj go do
decyzji ratunkowych, medycznych, prawnych ani innych decyzji wysokiego ryzyka.

<!-- mike-doc:install -->
## Instalacja

Wymagania: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama i około
15–25 GB wolnego miejsca zależnie od modeli. Repozytorium nie zawiera modeli ani
mediów. OmniVoice działa w osobnym środowisku, aby nie kolidować z Whisperem.

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

Dla wariantu OpenAI Whisper/PyTorch użyj `.[voice,torch,overlay]`. Kod OmniVoice
ma licencję Apache-2.0, ale domyślny model ma licencję **CC-BY-NC i nie jest
przeznaczony do użytku komercyjnego**. Model pobiera się przy pierwszym starcie
usługi i nie jest częścią repozytorium.

<!-- mike-doc:first-run -->
## Pierwsze uruchomienie

Uruchom `.venv/bin/mike start`, a następnie `.venv/bin/mike status`. Pierwszy
start może pobrać modele. Panel działa wyłącznie pod
`http://127.0.0.1:8140/`, a OmniVoice pod `http://127.0.0.1:8130/`. Przy kolizji
portu lub starego procesu M.I.K.E. zatrzyma się z wyjaśnieniem i nie zmieni
starszej instalacji.

<!-- mike-doc:permissions -->
## Uprawnienia macOS

Przy pierwszym użyciu zezwól Pythonowi/M.I.K.E. na mikrofon w **Ustawienia
systemowe → Prywatność i ochrona → Mikrofon**. Po odmowie włącz dostęp ręcznie
i wykonaj `mike restart`. Overlay nie wymaga Accessibility ani Screen Recording;
uprawnienia administratora nie są potrzebne.

<!-- mike-doc:configuration -->
## Konfiguracja

Plik znajduje się w `~/Library/Application Support/MIKE/config.toml`; katalogi
mają tryb 700, a pliki danych 600. Ollama, dashboard i OmniVoice muszą pozostać
na loopbacku. Najważniejsze pola to `assistant.model`, `stt.backend`,
`stt.model`, `server.port`, `[features]` oraz:

```toml
[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0
```

Publiczne zmienne mają prefiks `MIKE_*`; `MIKE_HOME` izoluje test. Serwer
publiczny obsługuje wyłącznie projektowanie głosu, nie przyjmuje nagrania
wzorcowego i nie klonuje głosu. Voiceprint twórz tylko z własnego głosu lub za
wyraźną zgodą mówcy, potem ustaw `features.voiceprint = true`.

<!-- mike-doc:controls -->
## Sterowanie

Polecenia cyklu życia to `mike install|start|stop|restart|status|doctor|uninstall`.
Zwracaj się „Majku”; „Majku, stop” przerywa kolejkę OmniVoice. Pamięć używa
czeskich fraz „pamatuj si, že …” i „zapomeň na …”. Research oraz terminal są
opt-in. Terminal dopuszcza tylko wybrane polecenia read-only bez powłoki,
potoków, przekierowań i zapisu.

<!-- mike-doc:privacy -->
## Prywatność

Brak telemetrii. Dashboard, baza, Ollama, transkrypcja, voiceprint i OmniVoice
są lokalne. Surowe audio nie jest domyślnie zapisywane. Tymczasowy syntetyczny
WAV ma tryb 600 i jest usuwany po `afplay`; serwer nie przyjmuje głosu
wzorcowego. Włączenie research wysyła jawne zapytanie do wyszukiwarki i
wybranych publicznych stron HTTPS. Zobacz [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Rozwiązywanie problemów

Zacznij od `mike doctor`. Dla Ollamy sprawdź `ollama list` i
`assistant.model`. Dla OmniVoice uruchom `./scripts/omnivoice_service.sh status`,
sprawdź `omnivoice-error.log` i `tts.omnivoice_url`. Brak transkrypcji oznacza
konieczność sprawdzenia Mikrofonu i `stt.device`. Przy zajętym 8140 zmień
`server.port`. Starą instalację Whisper Flow/MAJKA zatrzymuj wyłącznie jej
własnym narzędziem.

<!-- mike-doc:uninstall -->
## Odinstalowanie

Uruchom `.venv/bin/mike stop`, `.venv/bin/mike uninstall` oraz
`./scripts/omnivoice_service.sh uninstall`. Usuwane są tylko LaunchAgenty
`io.github.emperorkundis.mike` i `io.github.emperorkundis.mike.omnivoice`;
dane pozostają do odzyskania. Po sprawdzeniu kopii zapasowej możesz przenieść
`~/Library/Application Support/MIKE` do Kosza. Starsze instalacje pozostają bez zmian.

<!-- mike-doc:warning -->
## Ograniczenia i licencje

v0.1.1 obsługuje tylko Apple Silicon macOS i czeski runtime. Transkrypcje i
odpowiedzi mogą być błędne; ważne działania musi nadzorować człowiek. Kod M.I.K.E.
jest MIT, a informacje o stronach trzecich są w
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Domyślny model OmniVoice
jest CC-BY-NC i nie może być używany komercyjnie. Zabronione są nieautoryzowane
naśladowanie głosu, podszywanie się i oszustwa. Brak binariów i publikacji PyPI.
