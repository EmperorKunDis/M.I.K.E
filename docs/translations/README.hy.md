# M.I.K.E. — հայերեն ուղեցույց

[Կանոնական չեխերեն README](../../README.md)։ M.I.K.E.-ը տեղային, բաց կոդով
չեխերեն ձայնային օգնական է Apple Silicon Mac-ի համար։ Whisper-ը խոսքը
վերծանում է, տեղային Ollama-ն պատասխանում է, իսկ macOS `say`-ը կարդում է
պատասխանը։ **0.1 տարբերակը alpha է. ծրագիրը, վահանակը և ձայնային հրամանները
չեխերեն են։ Սա ամբողջ ուղեցույցի, ոչ թե միջերեսի թարգմանությունն է։** Մի
օգտագործեք արտակարգ, բժշկական, իրավական կամ բարձր ռիսկով որոշումների համար։

<!-- mike-doc:install -->
## Տեղադրում

Պահանջվում են macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama և
մոդելներից կախված մոտ 10–20 GB։ Մոդելներ ու մեդիա պահոցում ներառված չեն։

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

OpenAI Whisper/PyTorch fallback-ի համար օգտագործեք `.[voice,torch,overlay]`։
Whisper-ը, Ollama-ն և յուրաքանչյուր մոդել ունեն առանձին լիցենզիա ու պայմաններ։

<!-- mike-doc:first-run -->
## Առաջին գործարկում

Գործարկեք `.venv/bin/mike start`, ապա `.venv/bin/mike status`։ Առաջին անգամ
Whisper-ը կարող է ներբեռնել մոդելը։ Վահանակը միայն
`http://127.0.0.1:8140/` հասցեում է։ Պորտի կամ հին գործընթացի բախման դեպքում
M.I.K.E.-ը կկանգնի բացատրությամբ և չի կանգնեցնի կամ ջնջի հին տեղադրումը։

<!-- mike-doc:permissions -->
## macOS թույլտվություններ

Թույլատրեք Python/M.I.K.E.-ը **System Settings → Privacy & Security →
Microphone** բաժնում։ Մերժումից հետո միացրեք և կատարեք `mike restart`։ Overlay-ը
չի պահանջում Accessibility կամ Screen Recording։ Admin իրավունք պետք չէ։

<!-- mike-doc:configuration -->
## Կարգավորում

Ֆայլը `~/Library/Application Support/MIKE/config.toml` է. պանակները 700,
տվյալների ֆայլերը 600 ռեժիմով են։ Ollama-ն ու dashboard-ը loopback են։
Research-ը, terminal-ը և voiceprint-ը անջատված են, telemetry չկա, raw audio-ն
չի պահվում։ Հիմնական դաշտերն են `assistant.model`, `stt.backend`, `stt.model`,
`stt.device`, `server.port`, `[features]`։ `MIKE_HOME`-ը մեկուսացնում է թեստը,
հանրային փոփոխականները `MIKE_*` են։

Voiceprint-ը ստեղծեք տեղային՝
`python -m mike.voiceprint /ուղի/ձեր-ձայնին.wav`, ապա միացրեք
`features.voiceprint = true`։ Օգտագործեք միայն սեփական ձայնը կամ հստակ համաձայնություն։

<!-- mike-doc:controls -->
## Կառավարում

Հրամաններ՝ `mike install|start|stop|restart|status|doctor|uninstall`։ Օգնականին
չեխերեն դիմեք «Majku», իսկ «Majku, stop»-ը դադարեցնում է խոսքը։ Հիշողություն՝
«pamatuj si, že X je Y» և «zapomeň na X»։ Research-ը պահանջում է opt-in և
«ověř na internetu …»։ Read-only terminal-ի համար պետք է թույլատրելի root և
«v terminálu spusť …»։ Shell, pipe, redirect և գրառում չեն աջակցվում։

<!-- mike-doc:privacy -->
## Գաղտնիություն

Telemetry չկա։ Dashboard-ը, Ollama-ն, բազան, transcription-ը և voiceprint-ը
տեղային են։ Raw audio-ն լռելյայն չի պահվում. private SQLite-ը պահում է տեքստը,
պատասխանները, բացահայտ հիշողությունն ու գնահատականները։ Միացված research-ը
միայն բացահայտ հարցումն է ուղարկում որոնիչին և ընտրված public HTTPS կայքերին։
Տես [PRIVACY.md](../../PRIVACY.md)։

<!-- mike-doc:troubleshooting -->
## Խնդիրների լուծում

Սկսեք `mike doctor`-ից։ Ollama-ն գործարկեք, ստուգեք `ollama list` և
`assistant.model`։ Եթե տեքստ չկա, ստուգեք Microphone-ը և `stt.device`-ը.
դատարկ արժեքը system input է։ Զբաղված 8140-ի դեպքում փոխեք `server.port`։ Հին
Whisper Flow/MAJKA-ն կանգնեցրեք իր գործիքով։ Log-երը
`~/Library/Application Support/MIKE/logs/`-ում են. կիսվելուց առաջ հանեք անձնական տվյալները։

<!-- mike-doc:uninstall -->
## Հեռացում

Կատարեք `.venv/bin/mike stop` և `.venv/bin/mike uninstall`։ Հեռացվում է միայն
LaunchAgent `io.github.emperorkundis.mike`-ը, տվյալները մնում են վերականգնման
համար։ Լրիվ ջնջելու համար backup-ը ստուգելուց հետո
`~/Library/Application Support/MIKE` պանակը տեղափոխեք Trash։ Հին տեղադրումը չի փոխվում։

<!-- mike-doc:warning -->
## Սահմանափակումներ և լիցենզիաներ

v0.1-ը աջակցում է միայն Apple Silicon macOS և չեխերեն runtime։ Տեքստն ու
պատասխանը կարող են սխալ լինել. կարևոր գործողությունները վերահսկում է մարդը։
Կոդը MIT է, վերագրումները՝ [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)։
Մոդելները, dependencies-ը և web աղբյուրներն ունեն իրենց լիցենզիաները. binary և PyPI չկան։
