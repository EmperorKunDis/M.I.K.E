# M.I.K.E. — ръководство на български

[Каноничният README на чешки](../../README.md). M.I.K.E. е локален асистент с
отворен код и чешки интерфейс за Mac с Apple Silicon. Whisper транскрибира
речта, локалният Ollama създава отговора, а локалният OmniVoice го произнася.
**Версия 0.1.1 е алфа: приложението, таблото и гласовите команди са на чешки;
този файл превежда цялото ръководство, а не интерфейса.** Не го използвайте за
спешни, медицински, правни или други решения с висок риск.

<!-- mike-doc:install -->
## Инсталиране

Изисквания: macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama и около
15–25 GB свободно място според моделите. Хранилището не съдържа модели или
медия. OmniVoice работи в отделна среда, за да не влиза в конфликт с Whisper.

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

За варианта OpenAI Whisper/PyTorch използвайте `.[voice,torch,overlay]`. Кодът
на OmniVoice е под Apache-2.0, но стандартният модел е под **CC-BY-NC и не е
предназначен за търговска употреба**. Той се изтегля при първото стартиране на
услугата и не е част от хранилището.

<!-- mike-doc:first-run -->
## Първо стартиране

Изпълнете `.venv/bin/mike start`, след това `.venv/bin/mike status`. При първото
стартиране може да се изтеглят модели. Таблото е достъпно само на
`http://127.0.0.1:8140/`, а OmniVoice — само на `http://127.0.0.1:8130/`. При
конфликт на порт или процес M.I.K.E. спира с обяснение, без да спира или изтрива
по-стара инсталация.

<!-- mike-doc:permissions -->
## Разрешения в macOS

При първата употреба разрешете микрофона за Python/M.I.K.E. в **Системни
настройки → Поверителност и сигурност → Микрофон**. След отказ го разрешете
ръчно и изпълнете `mike restart`. Overlay не изисква Accessibility или Screen
Recording, нито администраторски права.

<!-- mike-doc:configuration -->
## Конфигурация

Файлът е в `~/Library/Application Support/MIKE/config.toml`; директориите са с
режим 700, а файловете с данни — 600. Ollama, таблото и OmniVoice трябва да
останат на loopback. Основните полета са `assistant.model`, `stt.backend`,
`stt.model`, `server.port`, `[features]` и:

```toml
[tts]
enabled = true
omnivoice_url = "http://127.0.0.1:8130"
model = "k2-fsa/OmniVoice"
instruct = "male, middle-aged, low pitch"
num_steps = 32
speed = 1.0
```

Публичните променливи са с префикс `MIKE_*`; `MIKE_HOME` изолира тестовете.
Публичният сървър поддържа само проектиране на глас, не приема референтен запис
и не клонира гласове. Създавайте voiceprint само от собствен глас или с изричното
съгласие на говорещия.

<!-- mike-doc:controls -->
## Управление

Командите за жизнения цикъл са `mike install|start|stop|restart|status|doctor|uninstall`.
Обърнете се с „Majku“; „Majku, stop“ прекъсва опашката на OmniVoice. Паметта
използва чешките фрази „pamatuj si, že …“ и „zapomeň na …“. Research и терминалът
са по избор. Терминалът допуска само избрани команди само за четене, без shell,
pipe, пренасочване или запис.

<!-- mike-doc:privacy -->
## Поверителност

Няма телеметрия. Таблото, базата, Ollama, транскрипцията, voiceprint и OmniVoice
остават локални. Суровият звук не се записва по подразбиране. Временният
синтетичен WAV е с режим 600 и се изтрива след `afplay`; сървърът не приема
референтен глас. Включеният research изпраща изрична заявка към търсачка и
избрани публични HTTPS страници. Вижте [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Отстраняване на проблеми

Започнете с `mike doctor`. За Ollama проверете `ollama list` и
`assistant.model`. За OmniVoice изпълнете `./scripts/omnivoice_service.sh status`
и проверете `omnivoice-error.log` и `tts.omnivoice_url`. Ако няма транскрипция,
проверете разрешението за микрофона и `stt.device`. При зает порт 8140 променете
`server.port`. Спирайте стара Whisper Flow/MAJKA инсталация само с нейния
собствен инструмент.

<!-- mike-doc:uninstall -->
## Деинсталиране

Изпълнете `.venv/bin/mike stop`, `.venv/bin/mike uninstall` и
`./scripts/omnivoice_service.sh uninstall`. Премахват се само LaunchAgent-ите
`io.github.emperorkundis.mike` и `io.github.emperorkundis.mike.omnivoice`;
данните остават за възстановяване. След проверка на архива можете да преместите
`~/Library/Application Support/MIKE` в Кошчето. По-старите инсталации не се променят.

<!-- mike-doc:warning -->
## Ограничения и лицензи

v0.1.1 поддържа само Apple Silicon macOS и чешки runtime. Транскрипцията и
отговорът може да са грешни; важните действия трябва да се контролират от човек.
Кодът на M.I.K.E. е под MIT, а известията за трети страни са в
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Стандартният модел
OmniVoice е CC-BY-NC и не може да се използва търговски. Забранени са
неразрешено имитиране на глас, представяне за друг човек и измама. Няма бинарни
файлове и няма публикация в PyPI.
