# M.I.K.E. — беларуская інструкцыя

[Кананічны README па-чэшску](../../README.md). M.I.K.E. — лакальны адкрыты
чэшскі галасавы памочнік для Mac з Apple Silicon. Whisper распазнае маўленне,
лакальная Ollama стварае адказ, а лакальны OmniVoice агучвае яго. **Версія 0.1.1 — alpha:
праграма, панэль і галасавыя каманды працуюць па-чэшску. Гэта поўны пераклад
інструкцыі, а не runtime.** Не выкарыстоўвайце памочнік для экстранных,
медыцынскіх, юрыдычных або іншых рашэнняў высокай рызыкі.

<!-- mike-doc:install -->
## Усталяванне

Патрэбны macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama і каля
10–20 ГБ у залежнасці ад мадэляў. Мадэлі і медыя не ўваходзяць у рэпазіторый.

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

Для OpenAI Whisper/PyTorch fallback выкарыстоўвайце `.[voice,torch,overlay]`.
Whisper, Ollama і кожная мадэль маюць асобныя ліцэнзіі і ўмовы.
OmniVoice працуе ў асобным `.venv-omnivoice`; код мае ліцэнзію Apache-2.0, але
стандартная мадэль — **CC-BY-NC і не для камерцыйнага выкарыстання**. Яна
спампоўваецца пры першым запуску службы і не ўваходзіць у рэпазіторый.

<!-- mike-doc:first-run -->
## Першы запуск

Выканайце `.venv/bin/mike start`, пасля `.venv/bin/mike status`. Першы Whisper
можа спампаваць мадэль. Панэль даступная толькі на `http://127.0.0.1:8140/`.
Пры канфлікце порта або старога працэсу M.I.K.E. спыніцца з тлумачэннем і не
будзе спыняць ці выдаляць ранейшую ўсталёўку.

<!-- mike-doc:permissions -->
## Дазволы macOS

Дазвольце Python/M.I.K.E. у **System Settings → Privacy & Security →
Microphone**. Калі доступ адхілены, уключыце яго і выканайце `mike restart`.
Overlay не патрабуе Accessibility або Screen Recording. Адміністратар не патрэбны.

<!-- mike-doc:configuration -->
## Канфігурацыя

Файл: `~/Library/Application Support/MIKE/config.toml`; каталогі маюць рэжым
700, файлы даных — 600. Ollama і dashboard выкарыстоўваюць loopback. Research,
terminal і voiceprint выключаны; тэлеметрыі няма, сырое аўдыя не захоўваецца.
Асноўныя палі: `assistant.model`, `stt.backend`, `stt.model`, `stt.device`,
`server.port`, `[features]`. `MIKE_HOME` ізалюе тэст; overrides маюць `MIKE_*`.

OmniVoice выкарыстоўвае `tts.omnivoice_url = "http://127.0.0.1:8130"`; палі
`tts.model`, `tts.instruct`, `tts.num_steps` і `tts.speed` кіруюць дызайнам
голасу. Публічны сервер не прымае эталоннае аўдыя і не клануе голас.

Стварыце voiceprint лакальна:
`python -m mike.voiceprint /шлях/да/ўласнага-голасу.wav`, пасля ўключыце
`features.voiceprint = true`. Выкарыстоўвайце толькі свой голас або відавочную
згоду чалавека.

<!-- mike-doc:controls -->
## Кіраванне

Каманды: `mike install|start|stop|restart|status|doctor|uninstall`. Зварот да
асістэнта — чэшскае «Majku»; «Majku, stop» перапыняе маўленне. Памяць: «pamatuj
si, že X je Y» і «zapomeň na X». Research патрабуе opt-in і «ověř na internetu
…». Read-only terminal патрабуе дазволены корань і «v terminálu spusť …»;
shell, pipe, перанакіраванне і запіс не падтрымліваюцца.

<!-- mike-doc:privacy -->
## Прыватнасць

Тэлеметрыі няма. Панэль, Ollama, база, транскрыпцыя і voiceprint лакальныя.
OmniVoice таксама лакальны: часовы сінтэтычны WAV мае рэжым 600 і выдаляецца
пасля `afplay`; сервер не прымае эталонны голас.
Сырое аўдыя па змаўчанні не запісваецца; прыватная SQLite захоўвае тэксты,
адказы, яўную памяць і ацэнкі. Уключаны research адпраўляе толькі яўны запыт
пошукавіку і выбраным публічным HTTPS-сайтам. Гл. [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Вырашэнне праблем

Пачніце з `mike doctor`. Для Ollama запусціце сэрвіс, праверце `ollama list` і
`assistant.model`. Без транскрыпцыі праверце Microphone і `stt.device`; пустое
значэнне — сістэмны ўваход. Пры занятым 8140 змяніце `server.port`. Старую
Whisper Flow/MAJKA спыняйце яе ўласным сродкам. Логі ў
`~/Library/Application Support/MIKE/logs/`; выдаліце асабістыя даныя перад перадачай.
Калі OmniVoice не працуе, выканайце `./scripts/omnivoice_service.sh status`,
праверце `omnivoice-error.log` і `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## Выдаленне

Выканаце `.venv/bin/mike stop` і `.venv/bin/mike uninstall`. Выдаляецца толькі
LaunchAgent `io.github.emperorkundis.mike`, даныя захоўваюцца. Для поўнага
выдалення пасля праверкі backup перанясіце `~/Library/Application Support/MIKE`
у Сметніцу. Ранейшыя ўсталёўкі не закранаюцца.
`./scripts/omnivoice_service.sh uninstall` выдаляе толькі асобны LaunchAgent
`io.github.emperorkundis.mike.omnivoice`.

<!-- mike-doc:warning -->
## Абмежаванні і ліцэнзіі

v0.1.1 падтрымлівае толькі Apple Silicon macOS і чэшскі runtime. Распазнаванне і
адказы могуць памыляцца; істотныя дзеянні кантралюе чалавек. Код — MIT,
атрыбуцыя ў [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Мадэлі,
залежнасці і web-крыніцы маюць свае ліцэнзіі; binary і PyPI release няма.
Стандартная мадэль OmniVoice мае CC-BY-NC і не дазваляе камерцыйнае выкарыстанне;
забаронены несанкцыянаванае перайманне голасу і махлярства.
