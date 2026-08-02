# M.I.K.E. — кыргызча колдонмо

[Чех тилиндеги негизги README](../../README.md). M.I.K.E. — Apple Silicon Mac
үчүн жергиликтүү, ачык коддуу чех үн жардамчысы. Whisper сүйлөөнү текстке
айлантат, жергиликтүү Ollama жооп берет, жергиликтүү OmniVoice аны үн чыгарат. **0.1.1 — alpha:
тиркеме, панель жана үн буйруктары чех тилинде. Бул интерфейстин эмес, толук
колдонмонун котормосу.** Өзгөчө кырдаал, медициналык, укуктук же жогорку
тобокел чечимдер үчүн колдонбоңуз.

<!-- mike-doc:install -->
## Орнотуу

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama жана моделге жараша
10–20 ГБ керек. Моделдер жана медиа репозиторийде жок.

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

OpenAI Whisper/PyTorch fallback үчүн `.[voice,torch,overlay]` колдонуңуз.
Whisper, Ollama жана ар бир моделдин өз лицензиясы жана шарттары бар.
OmniVoice өзүнчө `.venv-omnivoice` чөйрөсүндө иштейт; код Apache-2.0, ал демейки
модель **CC-BY-NC жана коммерциялык колдонууга арналган эмес**. Ал кызмат биринчи
иштегенде жүктөлөт жана репозиторийге кошулбайт.

<!-- mike-doc:first-run -->
## Биринчи иштетүү

`.venv/bin/mike start`, анан `.venv/bin/mike status` аткарыңыз. Whisper биринчи
жолу моделди жүктөшү мүмкүн. Панель `http://127.0.0.1:8140/` дарегинде гана.
Порт же эски процесс кагылышса, M.I.K.E. түшүндүрүп токтойт; эски орнотууну токтотпойт же өчүрбөйт.

<!-- mike-doc:permissions -->
## macOS уруксаттары

**System Settings → Privacy & Security → Microphone** бөлүмүндө Python/M.I.K.E.
үчүн уруксат бериңиз. Баш тартылса, күйгүзүп `mike restart` аткарыңыз. Overlay
Accessibility же Screen Recording талап кылбайт. Админ укугу кереги жок.

<!-- mike-doc:configuration -->
## Конфигурация

Файл `~/Library/Application Support/MIKE/config.toml`; каталогдор 700, маалымат
файлдары 600 режиминде. Ollama жана dashboard loopback колдонот. Research,
terminal, voiceprint өчүк; телеметрия жок, raw audio сакталбайт. Негизги талаалар:
`assistant.model`, `stt.backend`, `stt.model`, `stt.device`, `server.port`,
`[features]`. `MIKE_HOME` тестти бөлөт; өзгөрмөлөр `MIKE_*`.

OmniVoice `tts.omnivoice_url = "http://127.0.0.1:8130"` колдонот;
`tts.model`, `tts.instruct`, `tts.num_steps` жана `tts.speed` үн дизайнын
башкарат. Ачык сервер үлгү аудиону кабыл албайт жана үндү клондобойт.

Voiceprint жергиликтүү түзүңүз:
`python -m mike.voiceprint /оз-унунузга/жол.wav`, кийин
`features.voiceprint = true` коюңуз. Өз үнүңүздү же ачык макулдукту гана колдонуңуз.

<!-- mike-doc:controls -->
## Башкаруу

Буйруктар: `mike install|start|stop|restart|status|doctor|uninstall`. Жардамчыга
чехче «Majku» деп кайрылыңыз; «Majku, stop» сүйлөөнү токтотот. Эс: «pamatuj si,
že X je Y» жана «zapomeň na X». Research opt-in жана «ověř na internetu …»
талап кылат. Read-only terminal үчүн уруксат берилген root жана «v terminálu
spusť …» керек; shell, pipe, redirect жана жазуу жок.

<!-- mike-doc:privacy -->
## Купуялык

Телеметрия жок. Dashboard, Ollama, база, транскрипция жана voiceprint жергиликтүү.
Raw audio демейкиде сакталбайт; жеке SQLite текст, жооп, ачык эс жана бааларды
сактайт. Күйгүзүлгөн research ачык суроону гана издөө кызматына жана тандалган
ачык HTTPS сайттарга жөнөтөт. [PRIVACY.md](../../PRIVACY.md) караңыз.
OmniVoice да жергиликтүү: убактылуу синтетикалык WAV 600 режиминде түзүлүп,
`afplay`-ден кийин өчөт; сервер үлгү үндү кабыл албайт.

<!-- mike-doc:troubleshooting -->
## Көйгөйлөрдү чечүү

`mike doctor` менен баштаңыз. Ollama-ны иштетип, `ollama list` жана
`assistant.model` текшериңиз. Текст жок болсо, Microphone жана `stt.device`
текшериңиз; бош мааниси системалык кирүү. 8140 бош эмес болсо, `server.port`
өзгөртүңүз. Эски Whisper Flow/MAJKA-ны өз куралы менен токтотуңуз. Логдор
`~/Library/Application Support/MIKE/logs/` ичинде; бөлүшүүдөн мурда жеке маалыматты алып салыңыз.
OmniVoice жооп бербесе, `./scripts/omnivoice_service.sh status` аткарып,
`omnivoice-error.log` жана `tts.omnivoice_url` текшериңиз.

<!-- mike-doc:uninstall -->
## Өчүрүү

`.venv/bin/mike stop` жана `.venv/bin/mike uninstall` аткарыңыз. LaunchAgent
`io.github.emperorkundis.mike` гана өчөт; маалымат калыбына келтирүүгө калат.
Толук өчүрүү үчүн backup текшерип, `~/Library/Application Support/MIKE` папкасын
Trash-ка жылдырыңыз. Эски орнотуулар өзгөрбөйт.
`./scripts/omnivoice_service.sh uninstall` өзүнчө
`io.github.emperorkundis.mike.omnivoice` LaunchAgent-ин гана өчүрөт.

<!-- mike-doc:warning -->
## Чектөөлөр жана лицензиялар

v0.1.1 Apple Silicon macOS жана чех runtime гана колдойт. Текст же жооп жаңылыш
болушу мүмкүн; маанилүү аракетти адам көзөмөлдөйт. Код MIT, атрибуция
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Моделдер,
көз карандылыктар жана web булактардын өз лицензиялары бар; binary жана PyPI жок.
Демейки OmniVoice модели CC-BY-NC жана коммерция үчүн эмес; уруксатсыз үн
тууроо жана алдамчылыкка тыюу салынат.
