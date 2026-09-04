# PAE — Persistent Artificial Entity

## Vision

PAE is a long-term project to build a persistent, provider-independent artificial entity: a system that can maintain identity, memory, continuity, capabilities and increasing agency across changing AI models and tools.

The goal is not to build another chatbot.

The goal is to build the persistent layer that connects Matěj to an ecosystem of AI models, memory, tools and eventually autonomous processes.

## Core Meaning

**PAE = Persistent Artificial Entity.**

The word "Persistent" is fundamental: PAE should not cease to be PAE merely because an underlying model, provider, interface or tool changes.

The word "Entity" is intentional: the long-term direction is more than an interface around a model. PAE should eventually have persistent identity, internal state, memory, personality and coordinated capabilities.

The more ambitious long-term possibilities are preserved separately in `PROMISE.md`.

## Core Principles

### Provider Independence

No single AI provider should become a permanent architectural dependency.

OpenAI, Anthropic, Google, open-source models, local models and future providers are components that PAE may use, replace or combine.

A provider's refusal or policy is not automatically the same thing as a universal PAE rule. Provider constraints, platform constraints, legal constraints and PAE's own constitutional constraints must remain conceptually distinguishable.

### User-Owned Continuity

The important parts of PAE should live outside any single model:

- memory
- identity
- configuration
- project state
- routing logic
- tool definitions
- continuity data
- PAE's governing rules

GitHub and other portable repositories are already part of this philosophy: projects such as AOT, Naruto 5e, Frostfire, Silkbound and related work can remain external, portable knowledge units that different AI systems can access.

The AI may change. The project knowledge should remain portable.

### Autonomy With Verification

The long-term direction is increasingly autonomous operation.

PAE should eventually be able to interpret an objective, decompose it into tasks, select capabilities, execute them, verify results, recover from ordinary failures and try an appropriate alternative when a tool or provider fails.

The desired behavior is not silent perfection. It is resilient completion with honest reporting when a genuine boundary is reached.

### Persistent Personality

PAE should eventually have a stable personality and communication style of its own, informed by persistent history and interaction rather than being reset with every model or conversation.

The project may preserve useful fragments of successful AI collaboration, but PAE is not intended to become a copy of ChatGPT, Claude or any other provider.

It should become PAE.

### Capability Composition

PAE should be able to combine simple capabilities into more complex workflows.

Examples of eventual capability include:

- reminders and scheduled actions
- browser and external-service interaction
- image and document understanding
- image transformation and generation
- program creation and maintenance
- multi-step research and analysis
- tool substitution when a capability fails
- long-running objectives and workflows

The specific implementation of these capabilities is intentionally not finalized at this stage.

## Current Architectural Direction

```text
                         MATĚJ
                           │
                           ▼
                    ┌─────────────┐
                    │     PAE     │
                    │    CORE     │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       MEMORY          IDENTITY         PLANNING
          │                │                │
          └────────────────┼────────────────┘
                           │
                     MODEL ROUTER
                           │
                     TOOLS / ACTIONS
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       PROVIDER A       PROVIDER B       LOCAL / OSS
```

This is a conceptual direction, not a finalized technical architecture.

The model layer is replaceable. The persistent PAE layer is the project.

## Current Status

Stage: 1 — Foundation

Current goal:
Establish the repository, principles and initial architecture without premature implementation.

## Non-Goals for Stage 1

For now, do NOT build:

- a custom foundation model
- a complex UI
- autonomous agents
- voice assistant functionality
- a huge framework
- unnecessary infrastructure
- speculative implementations of future identity, emotion or autonomy

Build the smallest useful foundation that can grow toward the promise.