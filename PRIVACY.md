# Soukromí

M.I.K.E. je navržen jako lokální aplikace. Nemá telemetrii, reklamní ID,
cloudový účet ani automatické odesílání diagnostiky.

## Co ukládá

Pod `~/Library/Application Support/MIKE/` ukládá konfiguraci, SQLite databázi,
logy, explicitní paměť, hodnocení a případný hlasový otisk. Adresáře mají režim
700 a datové soubory 600. Surové audio je ve výchozím stavu vypnuté. Pokud
uživatel zapne `save_raw_audio`, ukládá se lokálně jako WAV s režimem 600.

## Co může opustit počítač

- Výchozí provoz používá pouze mikrofon, `127.0.0.1`, lokální Ollamu a lokální
  OmniVoice. Syntetický WAV existuje jen po dobu přehrání přes `afplay`, má
  režim 600 a služba jej následně smaže.
- Instalace závislostí a stahování Whisper/Ollama/OmniVoice modelů komunikuje s jejich
  distributory podle jejich zásad.
- Research je vypnutý. Po výslovném zapnutí a hlasovém požadavku odešle dotaz
  veřejnému vyhledávači a načte vybrané veřejné HTTPS stránky. Privátní,
  loopback a `.local` adresy jsou blokované.
- Read-only terminál nepoužívá síť s výjimkou explicitně povoleného lokálního
  `ollama list`; síťové git operace na allowlistu nejsou.

## Hlasový otisk

Hlasový embedding je biometrický údaj. Je opt-in, ukládá se pouze lokálně a
nesmí být vytvořen z cizí nahrávky bez výslovného souhlasu. Není neomylnou
autentizací a nesmí chránit vysoce rizikové operace.

## Syntéza hlasu

Veřejný OmniVoice server používá pouze obecný voice-design popis z konfigurace.
Nepřijímá referenční audio a neposkytuje endpoint pro klonování hlasu. Modelové
váhy se stahují samostatně a mají vlastní nekomerční licenci; nejsou součástí
repozitáře ani aplikačních dat M.I.K.E.

## Přístup, export a smazání

Dashboard zobrazuje lokální historii. `mike uninstall` data nemaže. Pro úplné
smazání nejprve zastavte a odinstalujte službu, potom po kontrole zálohy
přesuňte složku `~/Library/Application Support/MIKE` do Koše. Před hlášením
chyby z logu odstraňte přepisy a osobní údaje.
