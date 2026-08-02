# M.I.K.E. — o‘zbekcha qo‘llanma

[Chex tilidagi asosiy README](../../README.md). M.I.K.E. Apple Silicon Mac uchun
mahalliy, ochiq kodli chex ovozli yordamchisidir. Whisper nutqni matnga aylantiradi,
mahalliy Ollama javob beradi, macOS `say` javobni o‘qiydi. **0.1 alpha versiya:
ilova, panel va ovozli buyruqlar chex tilida. Bu interfeysning emas, to‘liq
qo‘llanmaning tarjimasi.** Favqulodda, tibbiy, huquqiy yoki yuqori xavfli
qarorlar uchun ishlatmang.

<!-- mike-doc:install -->
## O‘rnatish

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama va modelga qarab
taxminan 10–20 GB kerak. Modellar va media repozitoriyga kiritilmagan.

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

OpenAI Whisper/PyTorch fallback uchun `.[voice,torch,overlay]` dan foydalaning.
Whisper, Ollama va har bir modelning alohida litsenziyasi va shartlari bor.

<!-- mike-doc:first-run -->
## Birinchi ishga tushirish

`.venv/bin/mike start`, keyin `.venv/bin/mike status` bajaring. Whisper birinchi
marta model yuklashi mumkin. Panel faqat `http://127.0.0.1:8140/` manzilida.
Port yoki eski jarayon to‘qnashsa, M.I.K.E. izoh bilan to‘xtaydi; eski o‘rnatishni to‘xtatmaydi yoki o‘chirmaydi.

<!-- mike-doc:permissions -->
## macOS ruxsatlari

**System Settings → Privacy & Security → Microphone** bo‘limida Python/M.I.K.E.
uchun ruxsat bering. Rad etilgan bo‘lsa, yoqib `mike restart` bajaring. Overlay
Accessibility yoki Screen Recording talab qilmaydi. Admin huquqi kerak emas.

<!-- mike-doc:configuration -->
## Sozlash

Fayl `~/Library/Application Support/MIKE/config.toml`; kataloglar 700, ma’lumot
fayllari 600 rejimida. Ollama va dashboard loopback ishlatadi. Research,
terminal va voiceprint o‘chiq; telemetriya yo‘q, raw audio saqlanmaydi. Asosiy
maydonlar: `assistant.model`, `stt.backend`, `stt.model`, `stt.device`,
`server.port`, `[features]`. `MIKE_HOME` testni ajratadi; o‘zgaruvchilar `MIKE_*`.

Voiceprint-ni mahalliy yarating:
`python -m mike.voiceprint /oz-ovozingizga/yol.wav`, keyin
`features.voiceprint = true` qiling. Faqat o‘z ovozingiz yoki aniq rozilikdan foydalaning.

<!-- mike-doc:controls -->
## Boshqarish

Buyruqlar: `mike install|start|stop|restart|status|doctor|uninstall`. Yordamchiga
chexcha “Majku” deb murojaat qiling; “Majku, stop” nutqni to‘xtatadi. Xotira:
“pamatuj si, že X je Y” va “zapomeň na X”. Research opt-in va “ověř na
internetu …” talab qiladi. Read-only terminal uchun ruxsat etilgan root va “v
terminálu spusť …” kerak; shell, pipe, redirect va yozish yo‘q.

<!-- mike-doc:privacy -->
## Maxfiylik

Telemetriya yo‘q. Dashboard, Ollama, baza, transkripsiya va voiceprint mahalliy.
Raw audio sukut bo‘yicha saqlanmaydi; maxfiy SQLite matn, javob, aniq xotira va
baholarni saqlaydi. Yoqilgan research faqat aniq so‘rovni qidiruv xizmatiga va
tanlangan ochiq HTTPS saytlarga yuboradi. [PRIVACY.md](../../PRIVACY.md) ga qarang.

<!-- mike-doc:troubleshooting -->
## Muammolarni hal qilish

`mike doctor` bilan boshlang. Ollama-ni ishga tushirib `ollama list` va
`assistant.model` ni tekshiring. Matn bo‘lmasa, Microphone va `stt.device` ni
tekshiring; bo‘sh qiymat tizim kirishidir. 8140 band bo‘lsa, `server.port` ni
o‘zgartiring. Eski Whisper Flow/MAJKA-ni o‘z vositasi bilan to‘xtating. Loglar
`~/Library/Application Support/MIKE/logs/` ichida; ulashishdan oldin shaxsiy ma’lumotni olib tashlang.

<!-- mike-doc:uninstall -->
## O‘chirish

`.venv/bin/mike stop` va `.venv/bin/mike uninstall` bajaring. Faqat LaunchAgent
`io.github.emperorkundis.mike` o‘chadi; ma’lumot tiklash uchun qoladi. To‘liq
o‘chirish uchun backup-ni tekshirib `~/Library/Application Support/MIKE` jildini
Trash-ga ko‘chiring. Eski o‘rnatishlar o‘zgarmaydi.

<!-- mike-doc:warning -->
## Cheklovlar va litsenziyalar

v0.1 faqat Apple Silicon macOS va chex runtime-ni qo‘llaydi. Matn yoki javob
xato bo‘lishi mumkin; muhim harakatni inson nazorat qiladi. Kod MIT, atribusiya
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) da. Modellar,
bog‘liqliklar va web manbalarning o‘z litsenziyasi bor; binary va PyPI yo‘q.
