# M.I.K.E. — lietuviškas vadovas

[Kanoninis README čekų kalba](../../README.md). M.I.K.E. yra vietinis atvirojo
kodo čekų balso asistentas Apple Silicon Mac kompiuteriams. Whisper transkribuoja,
vietinė Ollama atsako, o vietinis OmniVoice jį įgarsina. **0.1.1 versija yra alfa:
programa, skydelis ir balso komandos yra čekų kalba. Tai visas vadovo, ne
sąsajos vertimas.** Nenaudokite skubiems, medicininiams, teisiniams ar kitiems
didelės rizikos sprendimams.

<!-- mike-doc:install -->
## Diegimas

Reikia macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama ir maždaug
10–20 GB, priklausomai nuo modelių. Modeliai ir medija į saugyklą neįtraukti.

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

OpenAI Whisper/PyTorch atsarginiam variantui naudokite `.[voice,torch,overlay]`.
Whisper, Ollama ir kiekvienas modelis turi savo licenciją ir sąlygas.
OmniVoice veikia atskiroje `.venv-omnivoice`; kodas yra Apache-2.0, tačiau
numatytasis modelis yra **CC-BY-NC ir neskirtas komerciniam naudojimui**. Jis
atsisiunčiamas pirmą kartą paleidus paslaugą ir į saugyklą neįtrauktas.

<!-- mike-doc:first-run -->
## Pirmasis paleidimas

Vykdykite `.venv/bin/mike start`, tada `.venv/bin/mike status`. Pirmą kartą
Whisper gali atsisiųsti modelį. Skydelis veikia tik
`http://127.0.0.1:8140/`. Jei konfliktuoja prievadas ar senas procesas, M.I.K.E.
sustos ir paaiškins; senos diegties nestabdys ir netrins.

<!-- mike-doc:permissions -->
## macOS leidimai

Leiskite Python/M.I.K.E. per **System Settings → Privacy & Security →
Microphone**. Jei prieiga atmesta, įjunkite ją ir vykdykite `mike restart`.
Overlay nereikia Accessibility ar Screen Recording. Administratoriaus teisių nereikia.

<!-- mike-doc:configuration -->
## Konfigūracija

Failas: `~/Library/Application Support/MIKE/config.toml`; katalogų režimas 700,
duomenų failų 600. Ollama ir dashboard naudoja loopback. Research, terminal ir
voiceprint išjungti; telemetrijos nėra, neapdorotas garsas nesaugomas. Pagrindai:
`assistant.model`, `stt.backend`, `stt.model`, `stt.device`, `server.port`,
`[features]`. `MIKE_HOME` izoliuoja testą, vieši kintamieji turi `MIKE_*`.

OmniVoice naudoja `tts.omnivoice_url = "http://127.0.0.1:8130"`; laukai
`tts.model`, `tts.instruct`, `tts.num_steps` ir `tts.speed` valdo balso dizainą.
Viešasis serveris nepriima etaloninio garso ir neklonuoja balso.

Voiceprint sukurkite vietoje:
`python -m mike.voiceprint /kelias/iki/savo-balso.wav`, tada nustatykite
`features.voiceprint = true`. Naudokite tik savo balsą arba aiškų kalbėtojo sutikimą.

<!-- mike-doc:controls -->
## Valdymas

Komandos: `mike install|start|stop|restart|status|doctor|uninstall`. Kreipinys
čekų kalba „Majku“; „Majku, stop“ nutraukia kalbą. Atmintis: „pamatuj si, že X
je Y“ ir „zapomeň na X“. Research reikia opt-in ir „ověř na internetu …“.
Read-only terminal reikia leistinos šaknies ir „v terminálu spusť …“; shell,
pipe, nukreipimai ir rašymas nepalaikomi.

<!-- mike-doc:privacy -->
## Privatumas

Telemetrijos nėra. Dashboard, Ollama, duomenų bazė, transkripcija ir voiceprint
yra vietiniai. Neapdorotas garsas pagal nutylėjimą nesaugomas; privati SQLite
saugo tekstus, atsakymus, aiškią atmintį ir įvertinimus. Įjungtas research siunčia
tik aiškią užklausą paieškai ir atrinktoms viešoms HTTPS svetainėms. Žr. [PRIVACY.md](../../PRIVACY.md).
OmniVoice taip pat vietinis: laikinas sintetinis WAV turi 600 režimą, po
`afplay` ištrinamas, o serveris nepriima etaloninio balso.

<!-- mike-doc:troubleshooting -->
## Trikčių šalinimas

Pradėkite `mike doctor`. Ollama paleiskite, patikrinkite `ollama list` ir
`assistant.model`. Jei nėra transkripcijos, patikrinkite Microphone ir
`stt.device`; tuščia reikšmė reiškia sistemos įvestį. Jei 8140 užimtas, keiskite
`server.port`. Seną Whisper Flow/MAJKA stabdykite jos įrankiu. Žurnalai yra
`~/Library/Application Support/MIKE/logs/`; prieš dalindamiesi pašalinkite asmens duomenis.
Jei OmniVoice neatsako, paleiskite `./scripts/omnivoice_service.sh status`,
patikrinkite `omnivoice-error.log` ir `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## Pašalinimas

Vykdykite `.venv/bin/mike stop` ir `.venv/bin/mike uninstall`. Pašalinamas tik
LaunchAgent `io.github.emperorkundis.mike`; duomenys lieka atkūrimui. Visiškai
ištrinti galima po atsarginės kopijos patikros perkeliant
`~/Library/Application Support/MIKE` į Trash. Senos diegtys neliečiamos.
`./scripts/omnivoice_service.sh uninstall` pašalina tik atskirą LaunchAgent
`io.github.emperorkundis.mike.omnivoice`.

<!-- mike-doc:warning -->
## Ribojimai ir licencijos

v0.1.1 palaiko tik Apple Silicon macOS ir čekišką runtime. Tekstas ir atsakymas
gali klysti; svarbias operacijas prižiūri žmogus. Kodas yra MIT, priskyrimai —
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Modeliai, priklausomybės
ir web šaltiniai turi savo licencijas; dvejetainių failų ir PyPI leidimo nėra.
Numatytasis OmniVoice modelis yra CC-BY-NC ir neskirtas komercijai; draudžiama
neteisėta balso imitacija ar sukčiavimas.
