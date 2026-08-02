# M.I.K.E. — ქართული სახელმძღვანელო

[კანონიკური ჩეხური README](../../README.md). M.I.K.E. არის ლოკალური, ღია კოდის
ჩეხური ხმოვანი ასისტენტი Apple Silicon Mac-ისთვის. Whisper მეტყველებას ტექსტად
აქცევს, ლოკალური Ollama პასუხობს, ხოლო ლოკალური OmniVoice პასუხს ახმოვანებს. **ვერსია
0.1.1 ალფაა: პროგრამა, პანელი და ხმოვანი ბრძანებები ჩეხურ ენაზეა. ეს არის სრული
სახელმძღვანელოს და არა ინტერფეისის თარგმანი.** არ გამოიყენოთ საგანგებო,
სამედიცინო, იურიდიული ან სხვა მაღალი რისკის გადაწყვეტილებებისთვის.

<!-- mike-doc:install -->
## ინსტალაცია

საჭიროა macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama და მოდელების
მიხედვით დაახლოებით 10–20 GB. მოდელები და მედია რეპოზიტორიაში არ შედის.

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

OpenAI Whisper/PyTorch fallback-ისთვის გამოიყენეთ `.[voice,torch,overlay]`.
Whisper-ს, Ollama-სა და თითოეულ მოდელს საკუთარი ლიცენზია და პირობები აქვს.
OmniVoice ცალკე `.venv-omnivoice` გარემოში მუშაობს; კოდი Apache-2.0-ია, მაგრამ
ნაგულისხმევი მოდელი **CC-BY-NC-ია და კომერციული გამოყენებისთვის არაა**. ის
სერვისის პირველი გაშვებისას იტვირთება და რეპოზიტორიაში არ შედის.

<!-- mike-doc:first-run -->
## პირველი გაშვება

გაუშვით `.venv/bin/mike start`, შემდეგ `.venv/bin/mike status`. პირველ ჯერზე
Whisper-მა შეიძლება მოდელი ჩამოტვირთოს. პანელი მხოლოდ
`http://127.0.0.1:8140/`-ზეა. პორტის ან ძველი პროცესის კონფლიქტისას M.I.K.E.
განმარტებით შეჩერდება და ძველ ინსტალაციას არ გააჩერებს ან წაშლის.

<!-- mike-doc:permissions -->
## macOS-ის ნებართვები

Python/M.I.K.E.-ს მიეცით წვდომა **System Settings → Privacy & Security →
Microphone**-ში. უარის შემდეგ ჩართეთ და გაუშვით `mike restart`. Overlay-ს არ
სჭირდება Accessibility ან Screen Recording. ადმინისტრატორის უფლება საჭირო არაა.

<!-- mike-doc:configuration -->
## კონფიგურაცია

ფაილია `~/Library/Application Support/MIKE/config.toml`; საქაღალდეები 700,
მონაცემთა ფაილები 600 რეჟიმითაა. Ollama და dashboard loopback-ს იყენებს.
Research, terminal და voiceprint გამორთულია; ტელემეტრია არაა და ნედლი აუდიო არ
ინახება. ძირითადი ველები: `assistant.model`, `stt.backend`, `stt.model`,
`stt.device`, `server.port`, `[features]`. `MIKE_HOME` ტესტს იზოლირებს; ცვლადებია `MIKE_*`.

OmniVoice იყენებს `tts.omnivoice_url = "http://127.0.0.1:8130"`; ველები
`tts.model`, `tts.instruct`, `tts.num_steps` და `tts.speed` ხმის დიზაინს მართავს.
საჯარო სერვერი საცნობარო აუდიოს არ იღებს და ხმას არ კლონავს.

Voiceprint ლოკალურად შექმენით:
`python -m mike.voiceprint /გზა/თქვენს-ხმამდე.wav`, შემდეგ ჩართეთ
`features.voiceprint = true`. გამოიყენეთ მხოლოდ საკუთარი ხმა ან აშკარა თანხმობა.

<!-- mike-doc:controls -->
## მართვა

ბრძანებები: `mike install|start|stop|restart|status|doctor|uninstall`. ასისტენტს
ჩეხურად მიმართეთ „Majku“; „Majku, stop“ საუბარს წყვეტს. მეხსიერება: „pamatuj
si, že X je Y“ და „zapomeň na X“. Research მოითხოვს opt-in-ს და „ověř na
internetu …“. Read-only terminal-ს სჭირდება დაშვებული root და „v terminálu
spusť …“; shell, pipe, redirect და ჩაწერა დაუშვებელია.

<!-- mike-doc:privacy -->
## კონფიდენციალურობა

ტელემეტრია არ არსებობს. Dashboard, Ollama, ბაზა, ტრანსკრიპცია და voiceprint
ლოკალურია. ნედლი აუდიო ნაგულისხმევად არ ინახება; პირადი SQLite ინახავს ტექსტს,
პასუხებს, აშკარა მეხსიერებას და შეფასებებს. ჩართული research მხოლოდ აშკარა
მოთხოვნას უგზავნის საძიებელს და შერჩეულ საჯარო HTTPS საიტებს. იხ. [PRIVACY.md](../../PRIVACY.md).
OmniVoice-იც ლოკალურია: დროებითი სინთეზური WAV 600 რეჟიმით იქმნება, `afplay`-ის
შემდეგ იშლება და სერვერი საცნობარო ხმას არ იღებს.

<!-- mike-doc:troubleshooting -->
## პრობლემების მოგვარება

დაიწყეთ `mike doctor`-ით. Ollama გაუშვით, შეამოწმეთ `ollama list` და
`assistant.model`. თუ ტექსტი არაა, შეამოწმეთ Microphone და `stt.device`; ცარიელი
მნიშვნელობა სისტემურ შესავალს ირჩევს. დაკავებული 8140-ისას შეცვალეთ
`server.port`. ძველი Whisper Flow/MAJKA საკუთარი ხელსაწყოთი გააჩერეთ. ლოგებია
`~/Library/Application Support/MIKE/logs/`; გაზიარებამდე პირადი მონაცემები წაშალეთ.
თუ OmniVoice არ პასუხობს, გაუშვით `./scripts/omnivoice_service.sh status`,
შეამოწმეთ `omnivoice-error.log` და `tts.omnivoice_url`.

<!-- mike-doc:uninstall -->
## დეინსტალაცია

გაუშვით `.venv/bin/mike stop` და `.venv/bin/mike uninstall`. იშლება მხოლოდ
LaunchAgent `io.github.emperorkundis.mike`; მონაცემები აღდგენისთვის რჩება.
სრული წაშლისთვის backup-ის შემოწმების შემდეგ
`~/Library/Application Support/MIKE` Trash-ში გადაიტანეთ. ძველი ინსტალაცია უცვლელია.
`./scripts/omnivoice_service.sh uninstall` მხოლოდ ცალკე LaunchAgent-ს
`io.github.emperorkundis.mike.omnivoice` შლის.

<!-- mike-doc:warning -->
## შეზღუდვები და ლიცენზიები

v0.1.1 მხოლოდ Apple Silicon macOS-სა და ჩეხურ runtime-ს უჭერს მხარს. ტექსტი და
პასუხი შეიძლება მცდარი იყოს; მნიშვნელოვან ქმედებას ადამიანი აკონტროლებს. კოდი
MIT-ია, ატრიბუცია — [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
მოდელებს, დამოკიდებულებებსა და web წყაროებს საკუთარი ლიცენზიები აქვთ; binary და PyPI არაა.
ნაგულისხმევი OmniVoice მოდელი CC-BY-NC-ია და კომერციული გამოყენებისთვის არაა;
აკრძალულია უნებართვო ხმის მიბაძვა და თაღლითობა.
