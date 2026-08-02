# Oznámení třetích stran

## Whisper Flow

Mikrofonní capture a část filtrace přepisu byly odvozeny z projektu
[Whisper Flow](https://github.com/dimastatz/whisper-flow), který je dostupný pod
licencí MIT:

> Copyright (c) 2024 Dima Statz

Úplné znění MIT licence je shodné se zněním v souboru [LICENSE](LICENSE).
Úpravy a veškerý nový kód M.I.K.E. jsou copyright (c) 2026 Martin Švanda.

## OpenAI Whisper

M.I.K.E. umí volitelně použít
[OpenAI Whisper](https://github.com/openai/whisper) distribuovaný pod MIT
licencí. Balíček ani modelové váhy nejsou součástí tohoto repozitáře.

## OmniVoice

M.I.K.E. komunikuje s lokálně instalovaným projektem
[k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice). Upstream zdrojový kód
je Apache-2.0. Výchozí předtrénovaný model
[`k2-fsa/OmniVoice`](https://huggingface.co/k2-fsa/OmniVoice) je podle jeho
model card licencován pod **CC-BY-NC** kvůli omezením trénovacích dat. Model
tedy není určen pro komerční použití a jeho váhy nejsou součástí tohoto MIT
repozitáře. Uživatel je stahuje přímo od distributora a odpovídá za dodržení
aktuální licence a zákazu neoprávněného klonování či napodobování hlasu.

## Modely a závislosti

`mlx-whisper`, modely z Hugging Face, Ollama, OmniVoice a jednotlivé modely se
stahují samostatně. Uživatel musí před použitím přijmout a dodržet jejich
aktuální licence, podmínky a případná omezení. Repozitář neobsahuje cizí model,
obrázek, zvuk, video, certifikát ani binární distribuční soubor.
