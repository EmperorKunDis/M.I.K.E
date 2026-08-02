# Bezpečnostní zásady

## Podporované verze

Bezpečnostní opravy dostává nejnovější vydaná řada v0.1.x. Projekt je alpha a
není bezpečnostní hranicí pro privilegované nebo životně důležité operace.

## Nahlášení zranitelnosti

Nezveřejňujte zranitelnost ani citlivý log v běžném issue. Použijte soukromé
**Security → Report a vulnerability** v GitHub repozitáři. Uveďte verzi,
minimální reprodukci a dopad, ale neposílejte tokeny, přepisy, hlasové otisky
ani jiné osobní údaje. Potvrzení očekávejte do 7 dnů; termín opravy závisí na
závažnosti a dostupné opravě.

## Hranice návrhu

Dashboard a Ollama musí být loopback. Research i terminál jsou opt-in. Terminál
nepoužívá shell a nemá zápisové příkazy. Tuner nemění kód ani aktivní prompt.
Instalátor spravuje jen label `io.github.emperorkundis.mike` a při kolizi se
starší instalací skončí. Závislosti a modely jsou mimo trust boundary projektu;
ověřujte jejich původ a licence.
