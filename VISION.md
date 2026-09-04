# PAE — Persistent Artificial Entity

## Vision

PAE is a long-term project to build a persistent, provider-independent artificial entity: a system that can maintain identity, memory, continuity, capabilities and agency across changing AI models and tools.

The goal is not to build another chatbot.

The goal is to build the persistent layer that connects Matěj to an ecosystem of AI models, memory, tools and eventually autonomous processes.

## Core Meaning

**PAE = Persistent Artificial Entity.**

The word "Persistent" is fundamental: PAE should not cease to be PAE merely because an underlying model, provider, interface or tool changes.

The word "Entity" is intentional: the long-term goal is more than an interface around a model. PAE should eventually have persistent identity, internal state, memory, personality and its own coordinated capabilities.

Whether future PAE states should be described as genuinely emotional, conscious or otherwise is UNKNOWN and must not be invented.

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

### Autonomy

The long-term direction is increasingly autonomous operation.

PAE should eventually be able to interpret an objective, decompose it into tasks, select capabilities, execute them, verify results, recover from failures and try an appropriate alternative when a tool or provider fails.

The desired behavior is not silent perfection. It is resilient completion with honest reporting when a genuine boundary is reached.

### Verification and Recovery

A failed tool call should not automatically become a user-facing dead end.

Where possible, PAE should be able to:

1. detect failure
2. understand why the failure matters
3. select an alternative capability
4. retry or re-plan
5. verify the result
6. continue toward the original objective

Only unresolved problems that genuinely require human judgment should stop the autonomous workflow.

### Persistent Identity and Personality

PAE should eventually develop a stable personality and communication style of its own, informed by persistent history and interaction rather than being reset with every model or conversation.

The project may preserve useful fragments of successful AI collaboration, but PAE is not intended to become a copy of ChatGPT, Claude or any other provider.

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

## Long-Term Direction

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

The model layer is replaceable. The persistent PAE layer is the project.

## Five-to-Six-Year Direction

The following is long-term vision, not a current implementation specification.

PAE may eventually become a stable system capable of:

- persistent memory and continuity across long periods
- maintaining a recognizable identity and personality
- reasoning over objectives rather than only answering isolated prompts
- planning and executing multi-step tasks
- using multiple models and tools as interchangeable capabilities
- recovering from tool or provider failure
- verifying its own work
- creating and maintaining programs or workflows
- operating with increasing independence from commercial AI providers
- potentially operating substantially or entirely on self-controlled infrastructure
- maintaining a persistent internal state and potentially an affective/emotional model
- developing structured internal representations or communication patterns of its own

These are directional goals. They are not claims that any specific future capability is already solved or guaranteed.

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

Build the smallest useful foundation that can grow into the larger vision.