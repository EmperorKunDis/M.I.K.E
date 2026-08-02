# M.I.K.E.

Lokální open-source český hlasový asistent pro macOS na Apple Silicon. Přepisuje
řeč pomocí Whisperu, odpovídá přes lokální Ollamu a mluví přes lokální
OmniVoice. Nemá telemetrii a po samostatném stažení modelů ve výchozím runtime
neposílá nic na internet.

> **Stav v0.1.1 (alpha):** aplikace, dashboard a hlasové povely jsou zatím pouze
> česky. Překlady níže překládají celý návod, ne runtime. M.I.K.E. není určen pro
> nouzové, zdravotní, právní ani jiné vysoce rizikové rozhodování.

[MIT licence](LICENSE) · [Soukromí](PRIVACY.md) · [Bezpečnost](SECURITY.md) ·
[Přispívání](CONTRIBUTING.md) · [Dokumentace](docs/README.md)

## Jazyky dokumentace

Čeština je kanonická. Úplné překlady: [English](docs/translations/README.en.md),
[Українська](docs/translations/README.uk.md), [Беларуская](docs/translations/README.be.md),
[Polski](docs/translations/README.pl.md), [Slovenčina](docs/translations/README.sk.md),
[Deutsch](docs/translations/README.de.md), [Magyar](docs/translations/README.hu.md),
[Български](docs/translations/README.bg.md), [Română](docs/translations/README.ro.md),
[Eesti](docs/translations/README.et.md),
[Latviešu](docs/translations/README.lv.md), [Lietuvių](docs/translations/README.lt.md),
[ქართული](docs/translations/README.ka.md), [Հայերեն](docs/translations/README.hy.md),
[Azərbaycanca](docs/translations/README.az.md), [Қазақша](docs/translations/README.kk.md),
[Кыргызча](docs/translations/README.ky.md), [Тоҷикӣ](docs/translations/README.tg.md),
[Türkmençe](docs/translations/README.tk.md) a [Oʻzbekcha](docs/translations/README.uz.md).
Celkem jde o 20 úplných překladů vedle kanonické češtiny. Ruština součástí
projektu není.

## Co umí

- průběžný lokální přepis češtiny přes `mlx-whisper` nebo OpenAI Whisper;
- české odpovědi z uživatelem zvoleného modelu v lokální Ollamě;
- lokální OmniVoice TTS ve voice-design režimu, bez klonování nebo přibaleného hlasu;
- explicitní paměť, lokální fulltextové vybavení kontextu a dashboard;
- volitelný průhledný macOS overlay, detekce barge-in a opt-in hlasový otisk;
- hodnocení odpovědí a bezpečný tuner, který pouze navrhne změnu promptu a
  nikdy ji sám neaktivuje ani neupravuje zdrojový kód;
- opt-in internetový research s blokací privátních adres;
- opt-in hlasový read-only terminál s allowlistem; zápisové příkazy nejsou ve
  v0.1 podporované.

<!-- mike-doc:install -->
## Instalace

Požadavky: macOS 13 nebo novější, Mac s Apple Silicon, Python 3.11/3.12,
[Ollama](https://ollama.com/), Homebrew a přibližně 15–25 GB volného místa podle
zvolených modelů. Modely ani média nejsou v repozitáři. OmniVoice běží ve
vlastním virtuálním prostředí, aby nekolidoval s Whisperem.

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

Pro PyTorch fallback místo MLX nainstalujte `.[voice,torch,overlay]`. Whisper a
každý Ollama model mají vlastní licenci a podmínky; před stažením je zkontrolujte.
Kód OmniVoice je Apache-2.0, ale výchozí předtrénovaný model `k2-fsa/OmniVoice`
je **CC-BY-NC a není určen pro komerční použití**. Model se stáhne až při prvním
startu služby. Podrobnosti jsou v [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

<!-- mike-doc:first-run -->
## První spuštění

```bash
.venv/bin/mike start
.venv/bin/mike status
```

Po prvním startu počkejte na stažení Whisper modelu. Dashboard je pouze na
`http://127.0.0.1:8140/`. Ověření instalace zopakujte příkazem `mike doctor`.
OmniVoice API poslouchá pouze na `http://127.0.0.1:8130/`; jeho model může při
prvním startu několik desítek sekund nabíhat.
Při obsazeném portu nebo nalezené starší instalaci instalátor/start skončí s
vysvětlením; cizí proces nikdy nezastaví ani nesmaže.

<!-- mike-doc:permissions -->
## Oprávnění macOS

Při prvním použití povolte mikrofon procesu Python/M.I.K.E. v **Nastavení
systému → Soukromí a zabezpečení → Mikrofon**. Pokud byl přístup zamítnut,
zapněte jej tam ručně a spusťte `mike restart`. Overlay nepotřebuje
Accessibility ani Screen Recording. M.I.K.E. nevyžaduje administrátorská práva.
OmniVoice používá Apple GPU přes MPS a k přehrání pouze systémový `afplay`;
syntézu hlasu neprovádí systémové TTS.

<!-- mike-doc:configuration -->
## Konfigurace

Kanonická konfigurace je v
`~/Library/Application Support/MIKE/config.toml`; adresáře mají režim 700 a
soubory s daty režim 600. Nejdůležitější volby:

```toml
[assistant]
model = "gemma3:12b"
ollama_url = "http://127.0.0.1:11434"

[stt]
backend = "mlx"
model = "large-v3-turbo"
device = ""

[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0

[features]
research = false
terminal = false
terminal_roots = []
voiceprint = false

[privacy]
telemetry = false
save_raw_audio = false
```

Dashboard smí poslouchat jen na `127.0.0.1` nebo `::1`; Ollama i OmniVoice TTS
musí zůstat na loopbacku. Testovací izolaci lze provést proměnnou `MIKE_HOME`.
Veřejné overrides mají pouze prefix `MIKE_*`, včetně
`MIKE_OMNIVOICE_URL`; staré rozhraní není podporováno. `tts.instruct` popisuje
obecný navržený hlas. Veřejná služba nepřijímá referenční audio a neumí klonovat
hlas konkrétní osoby.

Hlasový otisk je citlivý biometrický údaj. Zapněte jej až po lokálním vytvoření:

```bash
MIKE_HOME="$HOME/Library/Application Support/MIKE" \
  .venv/bin/python -m mike.voiceprint /cesta/k/vlastnimu-hlasu.wav
```

Použijte jen vlastní hlas nebo nahrávku s výslovným souhlasem mluvčího.

<!-- mike-doc:controls -->
## Ovládání

Správa služby: `mike install`, `start`, `stop`, `restart`, `status`, `doctor` a
`uninstall`. Asistenta oslovte „Majku“. „Majku, stop“ přeruší právě probíhající
řeč. Paměť používá explicitní věty „Majku, pamatuj si, že X je Y“ a „Majku,
zapomeň na X“.

OmniVoice syntéza se řadí do lokální fronty a „Majku, stop“ volá její `/stop`.
Research se spustí jen po zapnutí a explicitní větě jako „Majku, ověř na
internetu …“. Read-only terminál vyžaduje `terminal = true`, alespoň jeden
`terminal_roots` a formulaci „Majku, v terminálu spusť git status“. Povoleny
jsou jen čtecí varianty vybraných příkazů bez shellu, přesměrování a pipe.

<!-- mike-doc:privacy -->
## Soukromí

Bez telemetrie. Dashboard, Ollama, OmniVoice i databáze jsou lokální. Surové audio se
standardně neukládá; ukládají se přepisy, odpovědi, explicitní paměť a anonymní
hodnocení do privátní SQLite databáze. OmniVoice vytvoří pro přehrání dočasný
syntetický WAV s režimem 600 a po `afplay` jej smaže. Zapnutý research odešle výslovný dotaz
vyhledávači a navštíveným veřejným HTTPS webům. Hlasový otisk neopouští počítač,
ale stále jde o biometrický údaj. Podrobnosti a smazání dat popisuje
[PRIVACY.md](PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Řešení problémů

- `mike doctor` ukáže chybějící Python, STT balíček, Ollamu/model, OmniVoice,
  oprávnění, kolizi a režimy souborů.
- „OmniVoice neodpovídá“: spusťte `./scripts/omnivoice_service.sh status`,
  zkontrolujte `omnivoice-error.log` a shodu `tts.omnivoice_url`.
- „Ollama neodpovídá“: spusťte aplikaci Ollama, zkontrolujte `ollama list` a
  název `assistant.model`.
- Žádný přepis: ověřte Mikrofon v Nastavení systému a `stt.device`; prázdná
  hodnota používá výchozí vstup.
- Port 8140 je obsazen: nastavte jiný `server.port` a znovu spusťte `mike start`.
- Starší Whisper Flow/MAJKA běží: ukončete ji jejím vlastním nástrojem. M.I.K.E.
  ji záměrně nemění.
- Logy jsou v `~/Library/Application Support/MIKE/logs/`. Před sdílením je
  zkontrolujte a odstraňte přepisy či osobní údaje.

<!-- mike-doc:uninstall -->
## Odinstalace

```bash
.venv/bin/mike stop
.venv/bin/mike uninstall
./scripts/omnivoice_service.sh uninstall
```

Odinstalace odstraní pouze LaunchAgent `io.github.emperorkundis.mike`. Data
ponechá pro obnovu; druhý příkaz odstraní pouze namespaced OmniVoice LaunchAgent
`io.github.emperorkundis.mike.omnivoice`. Chcete-li data odstranit, přesuňte složku
`~/Library/Application Support/MIKE` do Koše až po kontrole zálohy. Starší
Whisper Flow/MAJKA zůstane nedotčená.

<!-- mike-doc:warning -->
## Omezení a licence

v0.1.1 podporuje pouze macOS Apple Silicon a český runtime. Přepis i odpovědi se
mohou mýlit. Aplikace nesmí bez lidské kontroly řídit nebezpečné operace.
Zdrojový kód je pod MIT licencí. Atribuce převzatých MIT částí jsou v
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); modely, Python balíčky a webové
zdroje se řídí vlastními licencemi. OmniVoice model je CC-BY-NC; M.I.K.E. jeho
váhy nedistribuuje. Nepoužívejte TTS k neoprávněnému napodobování, podvodu nebo
jazykové manipulaci vydávané za skutečnou osobu.
