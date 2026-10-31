# PAE — přehled spouštění

Spouštěj z kořene zachovaného checkoutu. Před aktualizací existujícího telefonu zachyť místní změny.

| Launcher | Rozhraní | Backend | Výchozí session | Ověření |
|---|---|---|---|---|
| start-local.sh | CLI | Místní llama-server | local-brain-smoke | Starší běh doložen |
| start-mobile.sh | HTTP na 127.0.0.1:8765, Android obal | Místní llama-server | pae-mobile | Kód sjednocen; dnešní telefon netestován |
| start-groq.sh | CLI | Groq | groq-first-test | Starší odpověď doložena |
| start-groq-gpt-oss-20b.sh | CLI | Varianta Groq | groq-gpt-oss-20b | Připraven, živý test nepotvrzen |
| start-groq-qwen38.sh | CLI | Varianta Groq | groq-qwen38 | Připraven, živý test nepotvrzen |
| start-gemini.sh | CLI | Gemini kompatibilní endpoint | Podle skriptu | Připraven, živý test nepotvrzen |

Modelová ID ve skriptech jsou požadované konfigurace, nikoli dnešní důkaz dostupnosti. Přístup a limity poskytovatele ověř při použití.

- Repo local/mobile používá kontext 2048; pozdější historie hlásí telefonní nastavení 4096. Přesné dnešní bajty chybí. Konsolidace rozdíl neřeší přepsáním telefonu.
- Kořen instalace vybírá PAE_ROOT; výchozí je ~/PAE.
- Klíče a konfigurace zůstávají v ~/.config/pae, váhy v místním models/. Do zdrojové předávky nepatří.
- Každý launcher vybírá backend při startu. Přepínání za běhu není implementované.
- Mobilní launcher kontroluje hash modulů a webového rozhraní; jeho nová verze nebyla spuštěna na telefonu.
- Pomocné instalátory v prototype_v0 jsou uchované historické nástroje. Před opakováním porovnej cílové soubory. Existence helperů neprokazuje jejich instalaci.
