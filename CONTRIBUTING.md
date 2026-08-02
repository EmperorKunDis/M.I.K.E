# Přispívání

Příspěvky jsou vítané, zejména testy, opravy přístupnosti, bezpečnosti a českého
rozpoznávání. Otevřete issue dřív, než začnete velkou změnu architektury.

1. Forkněte repozitář a vytvořte krátkou větev.
2. Nainstalujte `pip install -e ".[dev]"` (pro přepis také
   `.[voice,mlx,overlay]`; OmniVoice testujte v odděleném `.[omnivoice]` venv).
3. Zachovejte bezpečné výchozí hodnoty: loopback, žádná telemetrie, žádné audio.
4. Spusťte `./scripts/verify.sh`.
5. V PR popište dopad, testy, modelové/licenční změny a použití AI nástrojů.

Nikdy necommitujte přepisy, databáze, biometrické embeddingy, modely, hlasové
reference, média,
certifikáty, klíče, `.env` ani osobní údaje. Nová síťová nebo zápisová schopnost
vyžaduje threat model, opt-in konfiguraci a test výchozího vypnutí. Zápisový
hlasový terminál není v rozsahu v0.1.
