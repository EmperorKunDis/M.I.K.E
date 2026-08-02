# M.I.K.E. — українська інструкція

[Канонічний README чеською](../../README.md). M.I.K.E. — локальний відкритий
чеський голосовий асистент для Mac з Apple Silicon: Whisper розпізнає мовлення,
локальна Ollama формує відповідь, а macOS `say` її озвучує. **Версія 0.1 є
альфа-версією; застосунок, панель і голосові команди працюють чеською. Цей файл
перекладає всю інструкцію, але не інтерфейс.** Не використовуйте систему для
екстрених, медичних, юридичних чи інших рішень із високим ризиком.

<!-- mike-doc:install -->
## Встановлення

Потрібні macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama та близько
10–20 ГБ залежно від моделей. Моделі й медіафайли не входять до репозиторію.

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

Для fallback OpenAI Whisper/PyTorch використайте `.[voice,torch,overlay]`.
Whisper, Ollama й кожна модель мають власні ліцензії та умови.

<!-- mike-doc:first-run -->
## Перший запуск

Виконайте `.venv/bin/mike start`, потім `.venv/bin/mike status`. Перший запуск
Whisper може завантажити модель. Панель доступна лише за адресою
`http://127.0.0.1:8140/`. За конфлікту порту або старого процесу програма
зупиниться з поясненням і ніколи не завершить та не видалить стару інсталяцію.

<!-- mike-doc:permissions -->
## Дозволи macOS

Дозвольте Python/M.I.K.E. у **System Settings → Privacy & Security →
Microphone**. Якщо доступ було відхилено, увімкніть його вручну й виконайте
`mike restart`. Overlay не потребує Accessibility чи Screen Recording. Права
адміністратора не потрібні.

<!-- mike-doc:configuration -->
## Налаштування

Файл: `~/Library/Application Support/MIKE/config.toml`; каталоги мають режим
700, файли даних — 600. Ollama й панель працюють на loopback. Research,
термінал і voiceprint вимкнені; телеметрії немає, сире аудіо не зберігається.
Основні поля: `assistant.model`, `stt.backend`, `stt.model`, `stt.device`,
`server.port` і `[features]`. Для ізольованого тесту є `MIKE_HOME`; публічні
змінні мають лише префікс `MIKE_*`.

Voiceprint створюється локально командою
`python -m mike.voiceprint /шлях/до/вашого-голосу.wav`, після чого ввімкніть
`features.voiceprint = true`. Використовуйте лише власний голос або запис із
явною згодою мовця.

<!-- mike-doc:controls -->
## Керування

Команди: `mike install|start|stop|restart|status|doctor|uninstall`. Звертайтеся
чеською «Majku»; «Majku, stop» перериває мовлення. Пам’ять керується чеськими
фразами «pamatuj si, že X je Y» та «zapomeň na X». Research потребує ввімкнення
й фрази «ověř na internetu …». Read-only термінал також потребує дозволеного
кореня й «v terminálu spusť …»; shell, pipe, перенаправлення та запис заборонені.

<!-- mike-doc:privacy -->
## Конфіденційність

Телеметрії немає. Панель, Ollama, база, транскрипція та voiceprint локальні.
За замовчуванням сире аудіо не записується; приватна SQLite зберігає тексти,
відповіді, явну пам’ять та оцінки. Увімкнений research надсилає лише явний
запит пошуковику й вибраним публічним HTTPS-сайтам. Див. [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Усунення проблем

Почніть з `mike doctor`. Для Ollama запустіть сервіс, перевірте `ollama list` і
`assistant.model`. Якщо немає тексту, перевірте дозвіл Microphone та
`stt.device`; порожнє значення означає системний вхід. Змініть `server.port`,
якщо 8140 зайнятий. Старий Whisper Flow/MAJKA зупиняйте його власним засобом.
Логи лежать у `~/Library/Application Support/MIKE/logs/`; перед передаванням
видаліть транскрипти й особисті дані.

<!-- mike-doc:uninstall -->
## Видалення

Виконайте `.venv/bin/mike stop` і `.venv/bin/mike uninstall`. Видаляється лише
LaunchAgent `io.github.emperorkundis.mike`; дані залишаються для відновлення.
Для повного видалення після перевірки резервної копії перемістіть каталог
`~/Library/Application Support/MIKE` до Кошика. Старі інсталяції не змінюються.

<!-- mike-doc:warning -->
## Обмеження та ліцензії

v0.1 підтримує лише Apple Silicon macOS і чеський runtime. Розпізнавання та
відповіді можуть бути хибними; важливі дії контролює людина. Код має MIT,
атрибуція — у [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Моделі,
залежності й веб-джерела мають власні ліцензії. Бінарних файлів і PyPI-релізу немає.
