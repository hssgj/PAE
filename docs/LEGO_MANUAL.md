# PAE — LEGO manuál skutečné stavby

**Postavený celek:** výběr šuplíku → existující provider → agent → uložená konverzace → restart. Stejný základ obsluhuje CLI i mobilní HTTP most.

Tento manuál doprovází [audit dílů](audit/2026-10-31-parts.md) a [strojový důkaz sestavení](audit/assembly-proof.json). Důkaz používá echo a místní HTTP simulátor; nepředstírá živý Qwen, Groq ani instalaci v telefonu.

## 🟩 Základna: ověř celé sestavení

Ze současného zdrojového checkoutu:

```sh
python tools/verify_assembly.py
```

Skript použije dočasnou kopii bez tvých klíčů a konverzací. Opravdu spustí CLI, uloží vstup, zdroj a odpověď, znovu otevře session, použije druhý testovací backend ve stejné session a ověří mobilní HTTP most i jeho restart. Dočasné procesy po sobě ukončí.

**Spoj drží, když:** výstup má passed=true a všechny uvedené kontroly prošly. Hodnoty real_llm_inference=false a phone_installation_verified=false zůstávají výslovně uvedené.

## 🟪 Šuplíky: vyber konfiguraci

```sh
python prototype_v0/app.py --list-profiles
```

Katalog je v config/model_profiles.json, validace v prototype_v0/model_profiles.py. Výpis nečte klíče a nevytváří session.

| Šuplík | Co skutečně znamená |
|---|---|
| echo | Funkční testovací backend; odpověď pouze opakuje vstup. |
| local-qwen | Připravené připojení k místnímu serveru z dosavadního launcheru. Modelový server ani váhy se tím nestartují. |
| groq | Připravená konfigurace a reference na existující klíč. Dnešní přístup a model nejsou nově živě ověřené. |
| gemini | Připravené připojení; vyžaduje ověřené modelové ID přes PAE_GEMINI_MODEL. Staré neověřené ID se nepřebírá jako funkční výchozí hodnota. |

**Spoj drží, když:** každý profil projde validací. Neplatný profil, chybějící model nebo klíč skončí chybou; jiný model se nevybere potají.

## 🟩 Zapojení: spusť CLI a zachovej paměť

```sh
python prototype_v0/app.py --profile echo --session lego
```

Napiš krátkou zprávu a ukonči příkazem /quit. Stejný příkaz pak spustí tutéž session. Příkaz /history ukáže uložené zprávy.

**Spoj drží, když:** historie přežije ukončení procesu. Session patří PAE; profil se vybírá nezávisle. Šuplík se vybírá při startu, nikoli za běhu chatu.

## 🟩 Druhé rozhraní: stejný základ pro mobilní most

Dočasný místní test s echo lze spustit ze zdrojového checkoutu:

```sh
PAE_PROFILE=echo python prototype_v0/mobile_server.py
```

Most nabízí /api/health, /api/runtime, /api/history a /api/chat na 127.0.0.1:8765. Ruční spuštění používá místní session pae-mobile; opakovatelný verify_assembly.py ji místo toho zkouší v dočasné kopii na volném portu. CLI a most sdílejí kód ukládání; jejich výchozí session mají různá jména.

**Spoj drží, když:** HTTP vstup vyvolá odpověď a po restartu mostu zůstane jeho historie. To je ověřené v testovacím prostředí. Android APK se sestavuje samostatně a jeho instalace není tímto dokázaná.

## 🟧 Skutečný mozek: až s konkrétním důkazem

Po porovnání skutečných telefonních souborů a ověření jeho modelového serveru použij local-qwen. Cloud vyžaduje skutečně dostupný model a tvoje existující přístupové údaje. Tyto části zůstávají připravené, dokud neproběhne skutečná odpověď od daného backendu.

context_tokens v profilu je deklarace kapacity a kontrola konfigurace. Nenahrazuje telefonní context_guard.py, tokenizer ani počítání skutečného vstupu. Repo profil používá 2048; historicky hlášené telefonní 4096 nepřebíráme odhadem.

**Další fyzický díl:** spustit tools/phone_inventory.py na skutečném telefonu a porovnat výsledek. Kvůli tomu neprovádět slepý pull/reset existující instalace.

## 🗃️ Díly, které teď do stavby nezapojujeme

Task Tree a semantic-playground jsou zachované pokusy. Instalátory /paste/profilingu/source focus zůstávají volitelné historické pomůcky. Neplatný Freebie ZIP zůstává v karanténě. Automatický fallback, přepínání za běhu a nový paměťový engine nejsou dokončené ani aktivované touto stavbou.
