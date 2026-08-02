# ADR 0002: Lokální OmniVoice TTS

- Stav: přijato
- Datum: 2026-08-02

## Kontext

Systémový hlas macOS nesplňuje požadovanou kvalitu. OmniVoice má kvalitnější
multilingvní syntézu, ale jeho PyTorch prostředí může kolidovat s Whisperem a
výchozí předtrénovaný model má nekomerční licenci.

## Rozhodnutí

M.I.K.E. používá OmniVoice jako jediný TTS backend přes loopback API
`127.0.0.1`. Model běží v samostatném virtuálním prostředí a namespaced
LaunchAgentu. Veřejný server podporuje pouze voice design, nikoli referenční
audio nebo klonování hlasu. Syntetický WAV je privátní a po přehrání se smaže.
Model ani média nejsou v Git historii.

## Důsledky

Uživatel musí samostatně nainstalovat OmniVoice a stáhnout model. Upstream kód
je Apache-2.0, ale výchozí model je CC-BY-NC a není vhodný pro komerční použití.
`mike doctor` považuje nedostupnou OmniVoice službu za chybu, je-li TTS zapnuté.
