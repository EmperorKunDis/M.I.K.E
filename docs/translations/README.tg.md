# M.I.K.E. — дастури тоҷикӣ

[README-и асосӣ ба забони чехӣ](../../README.md). M.I.K.E. ёвари овозии
маҳаллӣ ва кушодаасоси чехӣ барои Mac-и Apple Silicon аст. Whisper нутқро ба
матн мегузаронад, Ollama-и маҳаллӣ ҷавоб медиҳад ва macOS `say` онро мехонад.
**Версияи 0.1 alpha аст: барнома, панел ва фармонҳои овозӣ чехӣ мебошанд. Ин
тарҷумаи пурраи дастур аст, на интерфейс.** Барои ҳолатҳои фаврӣ, тиббӣ, ҳуқуқӣ
ё қарорҳои хавфи баланд истифода набаред.

<!-- mike-doc:install -->
## Насб

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama ва вобаста ба модел
тақрибан 10–20 ГБ лозим аст. Модел ва медиа дар репозиторий нест.

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

Барои OpenAI Whisper/PyTorch fallback аз `.[voice,torch,overlay]` истифода
баред. Whisper, Ollama ва ҳар модел иҷозатнома ва шартҳои худро доранд.

<!-- mike-doc:first-run -->
## Оғози аввал

`.venv/bin/mike start`, баъд `.venv/bin/mike status`-ро иҷро кунед. Whisper
метавонад бори аввал моделро бор кунад. Панел танҳо дар
`http://127.0.0.1:8140/` аст. Ҳангоми бархӯрди порт ё раванди кӯҳна M.I.K.E. бо
шарҳ меистад ва насби кӯҳнаро намебандад ё пок намекунад.

<!-- mike-doc:permissions -->
## Иҷозатҳои macOS

Дар **System Settings → Privacy & Security → Microphone** ба Python/M.I.K.E.
иҷозат диҳед. Агар рад шуда бошад, фаъол карда `mike restart` иҷро кунед.
Overlay ба Accessibility ё Screen Recording ниёз надорад. Ҳуқуқи admin лозим нест.

<!-- mike-doc:configuration -->
## Танзим

Файл `~/Library/Application Support/MIKE/config.toml`; папкаҳо 700 ва файлҳои
маълумот 600 мебошанд. Ollama ва dashboard loopback истифода мебаранд. Research,
terminal ва voiceprint хомӯшанд; telemetry нест ва raw audio нигоҳ дошта
намешавад. Майдонҳо: `assistant.model`, `stt.backend`, `stt.model`, `stt.device`,
`server.port`, `[features]`. `MIKE_HOME` санҷишро ҷудо мекунад; тағйирёбандаҳо `MIKE_*`.

Voiceprint-ро маҳаллӣ созед:
`python -m mike.voiceprint /рох/ба/овози-худ.wav`, баъд
`features.voiceprint = true`. Танҳо овози худ ё ризоияти равшанро истифода баред.

<!-- mike-doc:controls -->
## Идоракунӣ

Фармонҳо: `mike install|start|stop|restart|status|doctor|uninstall`. Ба ёвар
бо чехӣ «Majku» гӯед; «Majku, stop» нутқро мебандад. Хотира: «pamatuj si, že X
je Y» ва «zapomeň na X». Research opt-in ва «ověř na internetu …» мехоҳад.
Read-only terminal root-и иҷозатшуда ва «v terminálu spusť …» мехоҳад; shell,
pipe, redirect ва навиштан дастгирӣ намешавад.

<!-- mike-doc:privacy -->
## Махфият

Telemetry нест. Dashboard, Ollama, база, транскрипсия ва voiceprint маҳаллӣ
мебошанд. Raw audio пешфарз нигоҳ дошта намешавад; SQLite-и хусусӣ матн, ҷавоб,
хотираи равшан ва баҳоро нигоҳ медорад. Research-и фаъол танҳо дархости равшанро
ба ҷустуҷӯ ва сайтҳои интихобшудаи HTTPS мефиристад. [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Ҳалли мушкилот

Аз `mike doctor` оғоз кунед. Ollama-ро оғоз карда `ollama list` ва
`assistant.model`-ро санҷед. Агар матн нест, Microphone ва `stt.device`-ро
санҷед; қимати холӣ вуруди система аст. Агар 8140 банд бошад, `server.port`-ро
иваз кунед. Whisper Flow/MAJKA-и кӯҳнаро бо асбоби худаш боздоред. Логҳо дар
`~/Library/Application Support/MIKE/logs/`; пеш аз мубодила маълумоти шахсиро гиред.

<!-- mike-doc:uninstall -->
## Поккунӣ

`.venv/bin/mike stop` ва `.venv/bin/mike uninstall` иҷро кунед. Танҳо LaunchAgent
`io.github.emperorkundis.mike` пок мешавад; маълумот барои барқарорӣ мемонад.
Барои поккунии пурра backup-ро санҷида `~/Library/Application Support/MIKE`-ро
ба Trash гузаронед. Насбҳои кӯҳна тағйир намеёбанд.

<!-- mike-doc:warning -->
## Маҳдудият ва иҷозатнома

v0.1 танҳо Apple Silicon macOS ва runtime-и чехиро дастгирӣ мекунад. Матн ва
ҷавоб метавонад хато шавад; амали муҳимро инсон назорат мекунад. Код MIT аст,
атрибутсия дар [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Моделҳо,
вобастагиҳо ва web-манбаъҳо иҷозатномаи худ доранд; binary ва PyPI нест.
