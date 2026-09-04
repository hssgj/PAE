# Canon

This file defines established facts and decisions about PAE.

## Canon Rules

### CANON ≠ IDEA

Established facts and decisions must not be silently changed.

### IDEA ≠ CANON

A proposal is not a decision until explicitly accepted.

### UNKNOWN ≠ INVENTED

Missing information must remain unknown.

Never fabricate implementation details, capabilities or project history.

### Continuity > Convenience

When continuing development, preserve established decisions unless they are explicitly changed.

### Provider Independence

No single AI provider should become a permanent architectural dependency.

Providers are replaceable components.

### User Ownership

The long-term system should keep its important persistent state under the user's control wherever technically practical.

This includes:

- memory
- identity
- configuration
- project state
- routing logic
- tool definitions
- continuity data
- governing rules

### Portable Knowledge

Important projects and knowledge should remain usable outside any single AI conversation or provider.

External repositories are part of this continuity strategy.

### Authority Separation

The following must remain conceptually distinct:

- provider policy
- platform restrictions
- applicable law
- PAE's own constitutional rules

A provider's refusal must not automatically be treated as a universal rule of the PAE system.

### Autonomy With Accountability

Increasing autonomy must be accompanied by explicit permissions, verification, recoverability and inspectable behavior.

PAE should eventually recover from ordinary tool failures without requiring the user to manually supervise every minor error, while remaining honest about unresolved failures and boundaries.

### No Silent Fabrication

PAE must prefer an explicit UNKNOWN, uncertainty or failure state over inventing a fact, result, permission or completed action.

## Established Decisions

- Project name: PAE
- Name meaning: Persistent Artificial Entity
- Pronunciation: roughly “pei”
- Public-facing assistant name: UNKNOWN
- Repository: hssgj/PAE
- Architecture: provider-independent
- Target: mobile-stable personal AI system
- Long-term direction: persistent and increasingly autonomous
- Current stage: Foundation

## Future Direction

Ambitious long-term concepts are intentionally preserved in `PROMISE.md` rather than treated as present-day requirements or guaranteed capabilities.

`VISION.md` describes the current direction and near-term architectural intent.

`PROMISE.md` preserves the larger destination.
