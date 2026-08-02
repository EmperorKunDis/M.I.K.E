# AGENTS.md

Toto je jediná autorita pro coding agenty v repozitáři M.I.K.E.

## Trust order

1. Aktuální zdroj a testy.
2. Tento soubor.
3. `docs/README.md`.
4. Přijaté ADR a `docs/current/system-context.md`.
5. Schválené specs/plány a runbooky.
6. Reviews a handovery jsou reference-only.

## Invarianty

- macOS Apple Silicon, Python 3.11+, český runtime;
- veřejné proměnné pouze `MIKE_*`; data pouze v privátním MIKE home;
- dashboard a Ollama pouze loopback; telemetrie a raw audio default off;
- research, terminál a voiceprint pouze opt-in; žádný zápisový terminál;
- TTS pouze přes lokální OmniVoice voice-design službu; žádné referenční audio,
  klonování nebo napodobování konkrétního hlasu;
- žádné modely, média, certifikáty, secrets, přepisy nebo osobní údaje v gitu;
- lifecycle aplikace spravuje jen `io.github.emperorkundis.mike`; OmniVoice
  helper jen `io.github.emperorkundis.mike.omnivoice`. Nikdy neukončují ani
  nemažou cizí/starší instalaci.

## Workflow

Před změnou čti `docs/README.md`, relevantní current/ADR/spec a testy. U změny
konfigurace, sítě, procesu, databáze nebo soukromí aktualizuj testy a dokumentaci.
Hotovo znamená `./scripts/verify.sh` a uživatelské ověření úměrné riziku.

Zastav se a vyžádej člověka při úniku tajemství/PII, změně výchozí síťové nebo
zápisové politiky, destruktivní migraci, publikaci, produkčním zásahu nebo růstu
scope mimo schválený plán. Neprováděj self-merge ani force push na `main`.
