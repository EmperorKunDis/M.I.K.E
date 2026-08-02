# M.I.K.E. — Azərbaycan dilində təlimat

[Çex dilində kanonik README](../../README.md). M.I.K.E. Apple Silicon Mac üçün
lokal, açıq mənbəli çex səsli köməkçidir. Whisper nitqi mətnə çevirir, lokal
Ollama cavab verir, macOS `say` isə cavabı səsləndirir. **0.1 alpha versiyadır:
proqram, panel və səs əmrləri çex dilindədir. Bu, interfeysin deyil, bütün
təlimatın tərcüməsidir.** Fövqəladə, tibbi, hüquqi və digər yüksək riskli
qərarlar üçün istifadə etməyin.

<!-- mike-doc:install -->
## Quraşdırma

macOS 13+, Apple Silicon, Python 3.11/3.12, Homebrew, Ollama və modeldən asılı
olaraq təxminən 10–20 GB tələb olunur. Modellər və media repozitoriyaya daxil deyil.

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

OpenAI Whisper/PyTorch fallback üçün `.[voice,torch,overlay]` istifadə edin.
Whisper, Ollama və hər modelin ayrıca lisenziyası və şərtləri var.

<!-- mike-doc:first-run -->
## İlk işə salma

`.venv/bin/mike start`, sonra `.venv/bin/mike status` işlədin. Whisper ilk dəfə
model yükləyə bilər. Panel yalnız `http://127.0.0.1:8140/` ünvanındadır. Port və
ya köhnə proses toqquşarsa, M.I.K.E. izahla dayanır; köhnə quraşdırmanı dayandırmır və silmir.

<!-- mike-doc:permissions -->
## macOS icazələri

**System Settings → Privacy & Security → Microphone** bölməsində Python/M.I.K.E.
üçün icazə verin. Rədd edilibsə, aktivləşdirin və `mike restart` işlədin. Overlay
Accessibility və Screen Recording tələb etmir. Admin hüququ lazım deyil.

<!-- mike-doc:configuration -->
## Konfiqurasiya

Fayl `~/Library/Application Support/MIKE/config.toml` yolundadır; qovluqlar 700,
məlumat faylları 600 rejimindədir. Ollama və dashboard loopback istifadə edir.
Research, terminal və voiceprint sönülüdür; telemetriya yoxdur, raw audio
saxlanmır. Əsas sahələr: `assistant.model`, `stt.backend`, `stt.model`,
`stt.device`, `server.port`, `[features]`. `MIKE_HOME` testi ayırır; dəyişənlər `MIKE_*`-dır.

Voiceprint-i lokal yaradın:
`python -m mike.voiceprint /oz-sesinize/yol.wav`, sonra
`features.voiceprint = true` edin. Yalnız öz səsinizdən və ya açıq razılıqdan istifadə edin.

<!-- mike-doc:controls -->
## İdarəetmə

Əmrlər: `mike install|start|stop|restart|status|doctor|uninstall`. Köməkçiyə çex
dilində “Majku” deyin; “Majku, stop” nitqi kəsir. Yaddaş üçün “pamatuj si, že X
je Y” və “zapomeň na X”. Research üçün opt-in və “ověř na internetu …” lazımdır.
Read-only terminal icazəli root və “v terminálu spusť …” tələb edir; shell,
pipe, redirect və yazma dəstəklənmir.

<!-- mike-doc:privacy -->
## Məxfilik

Telemetriya yoxdur. Dashboard, Ollama, baza, transkripsiya və voiceprint lokaldır.
Raw audio standart olaraq saxlanmır; məxfi SQLite mətnləri, cavabları, açıq
yaddaşı və qiymətləri saxlayır. Aktiv research yalnız açıq sorğunu axtarış
xidmətinə və seçilmiş açıq HTTPS saytlara göndərir. Baxın [PRIVACY.md](../../PRIVACY.md).

<!-- mike-doc:troubleshooting -->
## Problemlərin həlli

`mike doctor` ilə başlayın. Ollama-nı başladın, `ollama list` və
`assistant.model` yoxlayın. Mətn yoxdursa, Microphone və `stt.device` yoxlayın;
boş dəyər sistem girişidir. 8140 tutulubsa, `server.port` dəyişin. Köhnə Whisper
Flow/MAJKA-nı öz aləti ilə dayandırın. Loglar
`~/Library/Application Support/MIKE/logs/`-dadır; paylaşmadan şəxsi məlumatı silin.

<!-- mike-doc:uninstall -->
## Silmə

`.venv/bin/mike stop` və `.venv/bin/mike uninstall` işlədin. Yalnız LaunchAgent
`io.github.emperorkundis.mike` silinir; məlumat bərpa üçün qalır. Tam silmək
üçün backup-ı yoxlayıb `~/Library/Application Support/MIKE` qovluğunu Trash-a
köçürün. Köhnə quraşdırmalar dəyişmir.

<!-- mike-doc:warning -->
## Məhdudiyyətlər və lisenziyalar

v0.1 yalnız Apple Silicon macOS və çex runtime dəstəkləyir. Mətn və cavab səhv
ola bilər; vacib əməliyyata insan nəzarət etməlidir. Kod MIT-dir, atribusiya
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)-dədir. Modellər,
asılılıqlar və web mənbələrin öz lisenziyaları var; binary və PyPI yoxdur.
