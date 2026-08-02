# Architektura

```text
mikrofon -> audio segmenter -> Whisper backend -> filtry
                                              |
                                              v
dashboard/API -> Assistant -> paměť SQLite -> lokální Ollama -> OmniVoice klient
                                                                  |
                                                                  v
                                                    loopback server -> afplay
                      |              |
                      |              +-> judge -> pouze prompt candidate
                      +-> opt-in research / opt-in read-only terminál
```

`src/mike/config.py` je centrální validovaná konfigurace. `runtime.py` skládá
jediný proces a vlastní lock/PID. `dashboard.py` poslouchá jen na loopbacku.
`assistant.py` směruje explicitní paměť a volitelné schopnosti. `database.py`
ukládá text lokálně ve WAL SQLite. `launchd.py` spravuje jediný namespaced
LaunchAgent aplikace. Samostatný namespaced LaunchAgent OmniVoice odděluje jeho
PyTorch prostředí; API je pouze na `127.0.0.1`. Importy jsou jednosměrné;
poslední grafová kontrola neměla cykly.

Modely, OmniVoice a PyAudio/PyObjC jsou volitelné runtime závislosti. Importují se až při
použití, takže čisté CI nemusí stahovat modely ani získávat mikrofon.
