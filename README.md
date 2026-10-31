# PAE — Persistent Artificial Entity

**Začni v [LEGO manuálu skutečné stavby](docs/LEGO_MANUAL.md).** `main` je společný zdroj CLI i mobilní verze. [Rozcestník](docs/START_HERE.md) zachovává přehled zdrojů.

PAE je přenosný osobní AI runtime s trvalou konverzací a vyměnitelným modelem.

| Oblast | Kde je | Stav |
|---|---|---|
| Běhový kód a nástroje | [prototype_v0](prototype_v0/README.md) | CLI a mobilní kód sjednocené |
| Spouštění | [Launchery](docs/LAUNCHERS.md) | Lokální CLI, mobilní most a cloudové CLI |
| Android obal | [Mobilní instalace](MOBILE_SETUP.md), [pae-android](pae-android) | Zdroj zachovaný; instalace v telefonu vyžaduje ověření |
| Inventura a původ souborů | [Konsolidace](docs/consolidation/2026-10-31.md) | Ověřené snapshoty a otevřené mezery |
| Pravidla a pracovní stav | [discipline_os](discipline_os/BOOTSTRAP.md) | Autoritativní stav a protokoly |
| Pokusy a neplatné předávky | [archive](archive/README.md) | Oddělené od aktivního runtime |

Telefonní úpravy, modelové váhy, session a přístupy jsou místní data. Šuplíky pro výběr při startu jsou zapojené do runtime; přepínání za běhu zatím implementované není. Celou sestavenou kostru ověří `python tools/verify_assembly.py` bez cloudových klíčů.

Kanon: [CANON.md](CANON.md). Směr: [VISION.md](VISION.md). Dlouhodobá vize: [PROMISE.md](PROMISE.md). Další úložiště: [SYNC.md](SYNC.md).
