# M.I.K.E. — magyar útmutató

[A kanonikus cseh README](../../README.md). A M.I.K.E. helyi, nyílt forráskódú,
cseh nyelvű hangasszisztens Apple Silicon Mac gépekhez. A Whisper átírja a
beszédet, a helyi Ollama elkészíti a választ, a helyi OmniVoice pedig felolvassa.
**A 0.1.1 alfa verzióban az alkalmazás, az irányítópult és a hangparancsok cseh
nyelvűek; ez a fájl a teljes útmutatót fordítja le, nem a felületet.** Ne használja
vészhelyzeti, egészségügyi, jogi vagy más nagy kockázatú döntésekhez.

<!-- mike-doc:install -->
## Telepítés

Követelmények: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama és a
modellektől függően körülbelül 15–25 GB szabad hely. A tároló nem tartalmaz
modelleket vagy médiafájlokat. Az OmniVoice külön környezetben fut, hogy ne
ütközzön a Whisperrel.

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

Az OpenAI Whisper/PyTorch változathoz a `.[voice,torch,overlay]` csomagot
használja. Az OmniVoice kódja Apache-2.0 licencű, de az alapértelmezett modell
**CC-BY-NC licencű és kereskedelmi használatra nem alkalmas**. A modell a
szolgáltatás első indításakor töltődik le, és nem része a tárolónak.

<!-- mike-doc:first-run -->
## Első indítás

Futtassa a `.venv/bin/mike start`, majd a `.venv/bin/mike status` parancsot. Az
első indítás modelleket tölthet le. Az irányítópult csak a
`http://127.0.0.1:8140/`, az OmniVoice csak a `http://127.0.0.1:8130/` címen
érhető el. Port- vagy folyamatütközéskor a M.I.K.E. magyarázattal leáll, és nem
állítja le vagy törli a régebbi telepítést.

<!-- mike-doc:permissions -->
## macOS-engedélyek

Első használatkor engedélyezze a Python/M.I.K.E. mikrofonhozzáférését a
**Rendszerbeállítások → Adatvédelem és biztonság → Mikrofon** alatt. Elutasítás
után kapcsolja be kézzel, majd futtassa a `mike restart` parancsot. Az overlayhez
nem kell Kisegítő lehetőségek vagy Képernyőfelvétel, és rendszergazdai jog sem.

<!-- mike-doc:configuration -->
## Beállítás

A fájl helye `~/Library/Application Support/MIKE/config.toml`; a könyvtárak
jogosultsága 700, az adatfájloké 600. Az Ollama, az irányítópult és az OmniVoice
csak loopback címen futhat. Fő mezők: `assistant.model`, `stt.backend`,
`stt.model`, `server.port`, `[features]`, valamint:

```toml
[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0
```

A nyilvános változók előtagja `MIKE_*`; a `MIKE_HOME` elkülöníti a tesztet. A
nyilvános szerver csak hangtervezést támogat, referenciahangot nem fogad és
hangot nem klónoz. Voiceprintet csak saját hangból vagy a beszélő kifejezett
hozzájárulásával készítsen.

<!-- mike-doc:controls -->
## Vezérlés

Életciklus-parancsok: `mike install|start|stop|restart|status|doctor|uninstall`.
Az asszisztenst „Majku” megszólítással hívja; a „Majku, stop” megszakítja az
OmniVoice várólistáját. A memória cseh mondatai: „pamatuj si, že …” és
„zapomeň na …”. A kutatás és a terminál külön bekapcsolandó. A terminál csak
kijelölt, írásvédett parancsokat enged shell, pipe, átirányítás és írás nélkül.

<!-- mike-doc:privacy -->
## Adatvédelem

Nincs telemetria. Az irányítópult, az adatbázis, az Ollama, az átírás, a
voiceprint és az OmniVoice helyben marad. A nyers hang alapból nem tárolódik. Az
ideiglenes szintetikus WAV módja 600, az `afplay` után törlődik, és a szerver nem
fogad referenciahangot. A bekapcsolt kutatás kifejezett lekérdezést küld egy
keresőnek és kiválasztott nyilvános HTTPS-oldalaknak. Lásd:
[PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Hibaelhárítás

Kezdje a `mike doctor` paranccsal. Ollama esetén ellenőrizze az `ollama list` és
az `assistant.model` értékét. OmniVoice esetén futtassa a
`./scripts/omnivoice_service.sh status` parancsot, és nézze meg az
`omnivoice-error.log` fájlt meg a `tts.omnivoice_url` értékét. Átírás hiányában
ellenőrizze a Mikrofont és az `stt.device` mezőt. Foglalt 8140-es portnál
módosítsa a `server.port` értékét. A régi Whisper Flow/MAJKA telepítést csak a
saját eszközével állítsa le.

<!-- mike-doc:uninstall -->
## Eltávolítás

Futtassa a `.venv/bin/mike stop`, `.venv/bin/mike uninstall` és
`./scripts/omnivoice_service.sh uninstall` parancsokat. Csak az
`io.github.emperorkundis.mike` és az `io.github.emperorkundis.mike.omnivoice`
LaunchAgent törlődik; az adatok visszaállíthatók maradnak. Mentés ellenőrzése
után a `~/Library/Application Support/MIKE` a Kukába helyezhető. A régebbi
telepítések változatlanok maradnak.

<!-- mike-doc:warning -->
## Korlátok és licencek

A v0.1.1 csak Apple Silicon macOS rendszert és cseh runtime-ot támogat. Az
átírás és a válasz téves lehet; fontos műveleteket embernek kell felügyelnie. A
M.I.K.E. kódja MIT licencű, a külső összetevők adatai a
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) fájlban vannak. Az
alapértelmezett OmniVoice modell CC-BY-NC licencű és nem használható
kereskedelmi célra. Tilos az engedély nélküli hangutánzás, a megszemélyesítés és
a csalás. Nincsenek bináris fájlok és nincs PyPI-kiadás.
