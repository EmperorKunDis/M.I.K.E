# M.I.K.E. — eestikeelne juhend

[Kanooniline tšehhikeelne README](../../README.md). M.I.K.E. on lokaalne avatud
lähtekoodiga tšehhi häälassistent Apple Siliconiga Macile. Whisper transkribeerib,
lokaalne Ollama vastab ja macOS `say` loeb vastuse ette. **Versioon 0.1 on alfa:
rakendus, juhtpaneel ja häälkäsklused on tšehhi keeles. See fail on kogu juhendi,
mitte kasutajaliidese tõlge.** Ärge kasutage seda hädaolukorra, meditsiini,
õiguse ega muu kõrge riskiga otsuse jaoks.

<!-- mike-doc:install -->
## Paigaldamine

Vaja on macOS 13+, Apple Siliconit, Python 3.11/3.12, Homebrew’d, Ollamat ja
mudelitest sõltuvalt umbes 10–20 GB. Mudelid ja meedia pole repositooriumis.

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

OpenAI Whisper/PyTorchi varuvariandiks kasutage `.[voice,torch,overlay]`.
Whisperil, Ollamal ja igal mudelil on oma litsents ning tingimused.

<!-- mike-doc:first-run -->
## Esmakäivitus

Käivitage `.venv/bin/mike start` ja seejärel `.venv/bin/mike status`. Whisper
võib esimesel korral mudeli alla laadida. Juhtpaneel on ainult aadressil
`http://127.0.0.1:8140/`. Pordi või vana protsessi konflikti korral peatub
M.I.K.E. selgitusega ega lõpeta või kustuta vana paigaldust.

<!-- mike-doc:permissions -->
## macOS-i õigused

Lubage Python/M.I.K.E. menüüs **System Settings → Privacy & Security →
Microphone**. Keeldumise järel lubage juurdepääs käsitsi ja käivitage
`mike restart`. Overlay ei vaja Accessibility ega Screen Recording õigust.
Administraatori õigusi pole vaja.

<!-- mike-doc:configuration -->
## Seadistamine

Fail on `~/Library/Application Support/MIKE/config.toml`; kataloogid on 700 ja
andmefailid 600 õigustega. Ollama ning dashboard kasutavad loopbacki. Research,
terminal ja voiceprint on väljas; telemeetriat pole ja toorheli ei salvestata.
Põhiväljad: `assistant.model`, `stt.backend`, `stt.model`, `stt.device`,
`server.port`, `[features]`. `MIKE_HOME` eraldab testi; avalikud muutujad on `MIKE_*`.

Looge voiceprint lokaalselt käsuga
`python -m mike.voiceprint /tee/oma-haalele.wav` ja määrake seejärel
`features.voiceprint = true`. Kasutage ainult enda häält või kõneleja selget nõusolekut.

<!-- mike-doc:controls -->
## Juhtimine

Käsud: `mike install|start|stop|restart|status|doctor|uninstall`. Pöörduge
assistendi poole tšehhikeelse sõnaga „Majku”; „Majku, stop” katkestab kõne.
Mälu: „pamatuj si, že X je Y” ja „zapomeň na X”. Research vajab opt-in’i ja
„ověř na internetu …”. Read-only terminal vajab lubatud juurt ja „v terminálu
spusť …”; shell, pipe, ümbersuunamine ning kirjutamine pole lubatud.

<!-- mike-doc:privacy -->
## Privaatsus

Telemeetriat pole. Dashboard, Ollama, andmebaas, transkriptsioon ja voiceprint
on lokaalsed. Toorheli vaikimisi ei salvestata; privaatne SQLite säilitab teksti,
vastused, selgesõnalise mälu ja hinded. Lubatud research saadab ainult selge
päringu otsingule ning valitud avalikele HTTPS-saitidele. Vaadake [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Tõrkeotsing

Alustage `mike doctor` käsust. Ollama puhul käivitage teenus, kontrollige
`ollama list` ja `assistant.model`. Transkriptsiooni puudumisel kontrollige
Microphone õigust ja `stt.device`; tühi väärtus valib süsteemi sisendi. Kui 8140
on hõivatud, muutke `server.port`. Vana Whisper Flow/MAJKA peatage selle enda
tööriistaga. Logid on `~/Library/Application Support/MIKE/logs/`; eemaldage enne jagamist isikuandmed.

<!-- mike-doc:uninstall -->
## Eemaldamine

Käivitage `.venv/bin/mike stop` ja `.venv/bin/mike uninstall`. Eemaldatakse
ainult LaunchAgent `io.github.emperorkundis.mike`; andmed jäävad taastamiseks.
Täielikuks kustutamiseks teisaldage pärast varukoopia kontrolli
`~/Library/Application Support/MIKE` prügikasti. Vanad paigaldused ei muutu.

<!-- mike-doc:warning -->
## Piirangud ja litsentsid

v0.1 toetab ainult Apple Silicon macOS-i ja tšehhikeelset runtime’i. Tekst ning
vastus võivad eksida; olulist tegevust kontrollib inimene. Kood on MIT,
atributsioonid on [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
Mudelitel, sõltuvustel ja veebiallikatel on oma litsentsid; binaare ega PyPI-d pole.
