# PAE — skutečný výchozí bod

Stav po konsolidaci a sestavení dostupných dílů, 31. října 2026. **[LEGO manuál](LEGO_MANUAL.md)** obsahuje příkazy pro skutečně propojenou kostru a důkaz restartu.

**Kanonický kód je v hssgj/PAE, větev main.** CLI i mobilní most sdílejí stejnou smyčku, session a registr nástrojů. Starší mobilní větev je historický zdroj; její stavové soubory nepřepisují aktuální Discipline OS.

| Máme | Důkaz a hranice |
|---|---|
| CLI a mobilní most | Sloučený kód a regresní kontroly. Dnešní telefonní instalace nebyla spuštěna. |
| Trvalé session a zdroje | JSON úložiště; staré session bez pending_actions zůstávají načitatelné. |
| Lokální Qwen | Historicky ověřený offline běh; dnešní soubory a kontext na telefonu neznáme. |
| Cloudové CLI | Existující launchery a historická Groq odpověď. Aktuální přístup/modely nejsou tímto ověřené. |
| GitHub/Gmail nástroje | Zdroj z mobilní větve a zachované potvrzování zápisů a odeslání. Žádný e-mail nebyl při konsolidaci odeslán. |
| Archiv | Task Tree a staré laboratoře oddělené od runtime; neplatný Delivery Kit v karanténě. |

## Co ještě chybí

- Snapshot dnešního telefonu: zejména context_guard.py a místní app.py, provider.py, agent_loop.py a launchery.
- Přepínač během běžícího chatu a automatický fallback. Katalog modelů a výběr při startu jsou již zapojené a testované.
- Ověření přenosu přímo z Freebie. Čitelný test od ChatGPT ho nenahrazuje.
- Původní modelové konfigurační soubory a váhy; jejich seznam není záloha bajtů.

## Nejbližší krok

Na telefonu zachytit stav pomocí [phone_inventory.py](../tools/phone_inventory.py). Vytvoří místní ZIP; nic nenahrává, nemění checkout ani procesy. Session, váhy, klíčové soubory a zálohy nesbírá. Výstup před sdílením zkontroluj; vzorová kontrola tajných řetězců není zárukou odstranění všech citlivých údajů.

```sh
python tools/phone_inventory.py --include-source
```

Příkaz platí tam, kde už je nový skript dostupný. Kvůli jeho získání neprováděj slepý pull, switch ani reset existující instalace. Samostatně stažený skript přijímá `--root "$HOME/PAE"`.

Pak porovnat zachycené soubory s repem a zachovat místní změny. Před nasazením nových šuplíků do telefonu ověřit jeho skutečný výchozí stav; příprava a test katalogu ve zdrojovém checkoutu už proběhly.

- [Launchery](LAUNCHERS.md)
- [Rozsah konsolidace a zjištění](consolidation/2026-10-31.md)
- [Strojový registr zdrojů](consolidation/source-registry.json)
- [Mobilní instalace](../MOBILE_SETUP.md)
- [Archiv](../archive/README.md)

Tento rozcestník neurčuje novou trvalou prioritu a neaktivuje staré projekty.
