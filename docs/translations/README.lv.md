# M.I.K.E. — rokasgrāmata latviešu valodā

[Kanoniskais README čehu valodā](../../README.md). M.I.K.E. ir lokāls atvērtā
koda čehu balss asistents Apple Silicon Mac datoriem. Whisper pārvērš runu
tekstā, lokāla Ollama atbild, un lokāls OmniVoice to ierunā. **Versija 0.1.1 ir
alpha: lietotne, panelis un balss komandas ir čehu valodā. Šis ir pilns
rokasgrāmatas, nevis interfeisa tulkojums.** Nelietojiet ārkārtas, medicīniskiem,
juridiskiem vai citiem augsta riska lēmumiem.

<!-- mike-doc:install -->
## Instalēšana

Nepieciešams macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama un
apmēram 10–20 GB atkarībā no modeļiem. Modeļi un mediji nav repozitorijā.

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

OpenAI Whisper/PyTorch rezerves variantam lietojiet `.[voice,torch,overlay]`.
Whisper, Ollama un katram modelim ir sava licence un noteikumi.
OmniVoice darbojas atsevišķā `.venv-omnivoice`; kods ir Apache-2.0, bet
noklusējuma modelis ir **CC-BY-NC un nav paredzēts komerciālai lietošanai**.
Tas tiek lejupielādēts pirmajā pakalpojuma startā un nav iekļauts repozitorijā.

<!-- mike-doc:first-run -->
## Pirmā palaišana

Izpildiet `.venv/bin/mike start`, tad `.venv/bin/mike status`. Pirmajā reizē
Whisper var lejupielādēt modeli. Panelis pieejams tikai
`http://127.0.0.1:8140/`. Porta vai veca procesa konflikta gadījumā M.I.K.E.
apstājas ar skaidrojumu un neaptur vai nedzēš veco instalāciju.

<!-- mike-doc:permissions -->
## macOS atļaujas

Atļaujiet Python/M.I.K.E. sadaļā **System Settings → Privacy & Security →
Microphone**. Ja piekļuve noraidīta, ieslēdziet to un palaidiet `mike restart`.
Overlay neprasa Accessibility vai Screen Recording. Admin tiesības nav vajadzīgas.

<!-- mike-doc:configuration -->
## Konfigurācija

Fails ir `~/Library/Application Support/MIKE/config.toml`; direktorijām ir 700,
datu failiem 600 režīms. Ollama un dashboard izmanto loopback. Research,
terminal un voiceprint ir izslēgti; telemetrijas nav, neapstrādāts audio netiek
saglabāts. Galvenie lauki: `assistant.model`, `stt.backend`, `stt.model`,
`stt.device`, `server.port`, `[features]`. `MIKE_HOME` izolē testu, vides mainīgie ir `MIKE_*`.

OmniVoice izmanto `tts.omnivoice_url = "http://127.0.0.1:8130"`; lauki
`tts.model`, `tts.instruct`, `tts.num_steps` un `tts.speed` vada balss dizainu.
Publiskais serveris nepieņem atsauces audio un neklonē balsi.

Voiceprint izveidojiet lokāli:
`python -m mike.voiceprint /cels/uz/savu-balsi.wav`, pēc tam ieslēdziet
`features.voiceprint = true`. Izmantojiet tikai savu balsi vai skaidru runātāja piekrišanu.

<!-- mike-doc:controls -->
## Vadība

Komandas: `mike install|start|stop|restart|status|doctor|uninstall`. Asistentu
uzrunā čehu valodā “Majku”; “Majku, stop” pārtrauc runu. Atmiņai lieto “pamatuj
si, že X je Y” un “zapomeň na X”. Research prasa opt-in un “ověř na internetu
…”. Read-only terminal prasa atļautu sakni un “v terminálu spusť …”; shell,
pipe, pāradresācija un rakstīšana nav pieejama.

<!-- mike-doc:privacy -->
## Privātums

Telemetrijas nav. Dashboard, Ollama, datubāze, transkripcija un voiceprint ir
lokāli. Neapstrādāts audio pēc noklusējuma netiek glabāts; privāta SQLite glabā
tekstus, atbildes, skaidro atmiņu un vērtējumus. Ieslēgts research sūta tikai
skaidro vaicājumu meklētājam un atlasītām publiskām HTTPS vietnēm. Sk. [PRIVACY.md](../../PRIVACY.md).
Arī OmniVoice ir lokāls: pagaidu sintētiskajam WAV ir režīms 600, tas tiek
izdzēsts pēc `afplay`, un serveris nepieņem atsauces balsi.

<!-- mike-doc:troubleshooting -->
## Problēmu novēršana

Sāciet ar `mike doctor`. Ollama gadījumā palaidiet servisu, pārbaudiet
`ollama list` un `assistant.model`. Ja nav teksta, pārbaudiet Microphone un
`stt.device`; tukša vērtība nozīmē sistēmas ievadi. Ja 8140 aizņemts, mainiet
`server.port`. Veco Whisper Flow/MAJKA apturiet ar tās rīku. Logi ir
`~/Library/Application Support/MIKE/logs/`; pirms kopīgošanas noņemiet personas datus.
Ja OmniVoice neatbild, palaidiet `./scripts/omnivoice_service.sh status`,
pārbaudiet `omnivoice-error.log` un `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## Atinstalēšana

Izpildiet `.venv/bin/mike stop` un `.venv/bin/mike uninstall`. Tiek noņemts tikai
LaunchAgent `io.github.emperorkundis.mike`; dati paliek atjaunošanai. Pilnīgai
dzēšanai pēc rezerves kopijas pārbaudes pārvietojiet
`~/Library/Application Support/MIKE` uz Trash. Vecās instalācijas paliek neskartas.
`./scripts/omnivoice_service.sh uninstall` noņem tikai atsevišķo LaunchAgent
`io.github.emperorkundis.mike.omnivoice`.

<!-- mike-doc:warning -->
## Ierobežojumi un licences

v0.1.1 atbalsta tikai Apple Silicon macOS un čehu runtime. Transkripcija un atbilde
var kļūdīties; svarīgas darbības uzrauga cilvēks. Kods ir MIT, atribūcija ir
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Modeļiem, atkarībām un
tīmekļa avotiem ir savas licences; bināru un PyPI laidiena nav. Noklusējuma
OmniVoice modelis ir CC-BY-NC un nav komerciālai lietošanai; aizliegta neatļauta
balss atdarināšana un krāpšana.
