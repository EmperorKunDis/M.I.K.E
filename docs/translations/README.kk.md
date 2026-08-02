# M.I.K.E. — қазақша нұсқаулық

[Чех тіліндегі негізгі README](../../README.md). M.I.K.E. — Apple Silicon Mac
үшін жергілікті, ашық кодты чех дауыстық көмекшісі. Whisper сөйлеуді мәтінге
айналдырады, жергілікті Ollama жауап береді, macOS `say` оны оқиды. **0.1 — alpha:
қолданба, панель және дауыстық командалар чех тілінде. Бұл интерфейстің емес,
толық нұсқаулықтың аудармасы.** Төтенше, медициналық, заңдық немесе жоғары
тәуекелді шешімдер үшін қолданбаңыз.

<!-- mike-doc:install -->
## Орнату

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama және модельге қарай
шамамен 10–20 ГБ қажет. Модельдер мен медиа репозиторийге кірмейді.

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

OpenAI Whisper/PyTorch fallback үшін `.[voice,torch,overlay]` пайдаланыңыз.
Whisper, Ollama және әр модельдің жеке лицензиясы мен шарттары бар.

<!-- mike-doc:first-run -->
## Алғашқы іске қосу

`.venv/bin/mike start`, содан кейін `.venv/bin/mike status` орындаңыз. Whisper
алғашқы рет модель жүктеуі мүмкін. Панель тек `http://127.0.0.1:8140/` мекенінде.
Порт не ескі процесс қақтығысса, M.I.K.E. түсіндіріп тоқтайды; ескі орнатуды тоқтатпайды және жоймайды.

<!-- mike-doc:permissions -->
## macOS рұқсаттары

**System Settings → Privacy & Security → Microphone** бөлімінде Python/M.I.K.E.
үшін рұқсат беріңіз. Бас тартылса, қосып, `mike restart` орындаңыз. Overlay-ға
Accessibility немесе Screen Recording керек емес. Әкімші құқығы қажет емес.

<!-- mike-doc:configuration -->
## Баптау

Файл: `~/Library/Application Support/MIKE/config.toml`; каталог режимі 700,
дерек файлы 600. Ollama мен dashboard loopback қолданады. Research, terminal,
voiceprint өшірулі; телеметрия жоқ, raw audio сақталмайды. Негізгі өрістер:
`assistant.model`, `stt.backend`, `stt.model`, `stt.device`, `server.port`,
`[features]`. `MIKE_HOME` тестті оқшаулайды; орта айнымалылары `MIKE_*`.

Voiceprint-ті жергілікті жасаңыз:
`python -m mike.voiceprint /оз-дауысыныз/жолы.wav`, кейін
`features.voiceprint = true` қойыңыз. Тек өз дауысыңызды не айқын келісімді қолданыңыз.

<!-- mike-doc:controls -->
## Басқару

Командалар: `mike install|start|stop|restart|status|doctor|uninstall`.
Көмекшіге чехша «Majku» деңіз; «Majku, stop» сөйлеуді үзеді. Жад: «pamatuj si,
že X je Y» және «zapomeň na X». Research opt-in және «ověř na internetu …»
талап етеді. Read-only terminal үшін рұқсат етілген root және «v terminálu
spusť …» керек; shell, pipe, redirect және жазу жоқ.

<!-- mike-doc:privacy -->
## Құпиялық

Телеметрия жоқ. Dashboard, Ollama, база, транскрипция және voiceprint жергілікті.
Raw audio әдепкіде сақталмайды; жеке SQLite мәтін, жауап, айқын жад және бағаларды
сақтайды. Қосылған research тек айқын сұрауды іздеу қызметіне және таңдалған
ашық HTTPS сайттарына жібереді. [PRIVACY.md](../../PRIVACY.md) қараңыз.

<!-- mike-doc:troubleshooting -->
## Ақауларды шешу

`mike doctor`-дан бастаңыз. Ollama-ны іске қосып, `ollama list` пен
`assistant.model` тексеріңіз. Мәтін болмаса, Microphone және `stt.device`
тексеріңіз; бос мән жүйелік кіріс. 8140 бос болмаса, `server.port` ауыстырыңыз.
Ескі Whisper Flow/MAJKA-ны өз құралымен тоқтатыңыз. Логтар
`~/Library/Application Support/MIKE/logs/` ішінде; бөлісерде жеке деректі өшіріңіз.

<!-- mike-doc:uninstall -->
## Жою

`.venv/bin/mike stop` және `.venv/bin/mike uninstall` орындаңыз. Тек LaunchAgent
`io.github.emperorkundis.mike` жойылады; дерек қалпына келтіруге қалады. Толық
жою үшін backup тексеріп, `~/Library/Application Support/MIKE` қалтасын Trash-қа
жылжытыңыз. Ескі орнатулар өзгермейді.

<!-- mike-doc:warning -->
## Шектеулер мен лицензиялар

v0.1 тек Apple Silicon macOS және чех runtime қолдайды. Мәтін мен жауап қате
болуы мүмкін; маңызды әрекетті адам бақылайды. Код MIT, атрибуция
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) ішінде. Модельдер,
тәуелділіктер және web көздерінің өз лицензиясы бар; binary мен PyPI жоқ.
