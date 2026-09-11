# FitForm — Design

## Thesis

FitForm is a GenLayer Intelligent Contract on the **Lifeform** track:

> A self-evolving contract whose **bounded genome** (rules / parameters) updates only when multi-validator consensus agrees that fitness **improved** under a **sealed goal** and live public signal — not free-form LLM code rewrite.

It rewrites **its rules** on a loop. It does not deploy arbitrary mutated Python source as its identity.

## Track fit

Official idea: *Lifeform — a self-evolving contract that rewrites itself on a loop.*

FitForm interpretation:
- “Itself” = sealed goal + mutable genome (rule text, thresholds, policy params)
- “Rewrites on a loop” = anyone may call `evolve`; state advances only on consensus **IMPROVED**
- No human vote; no multi-sig council required for evolution

## Versus GenLayer Foundation Living Organism

| | Foundation Living Organism | FitForm |
|--|----------------------------|---------|
| What evolves | Full contract **source code** | Bounded **genome** (params / rule text) |
| Accept rule | Structural preserve (class, evolve, storage, …) | **IMPROVED** fitness vs sealed goal + signal |
| Deployment pattern | Always `deploy_contract` child generation | Same contract state update (v1); optional lineage later |
| Success signal | Novelty + valid structure | Measurable fitness increase |
| Failure mode | Broken child; parent intact | Reject evolve; genome unchanged |

FitForm is intentionally **stricter** on accept conditions and **narrower** on what may change.

## Non-goals

- Full Python source mutation / `exec` of model output as contract body
- Forcing non-integrating contracts
- Intelligent stablecoin / peg
- Emergency exploit halt (see HaltGate — separate product)
- Owner silently rewriting fitness or goal after deploy
- Mainnet SLA claims without audit and real integrators

## Adversarial model

| Attack | Mitigation |
|--------|------------|
| Clone / “already built” | Different mechanism; public vs-table; no source-factory identity |
| Fake IMPROVED prose | Closed labels only; comparative equivalence on `decision`; require `new_fitness > last_fitness` |
| Bad or empty fetch | Fail-closed → REJECTED; never IMPROVED on empty body |
| SSRF / bad hosts | Owner allowlist; HTTPS-only; reject IP, localhost, userinfo, `.local` |
| Evolve spam | Cooldown (`time.time()`); gas cost; v2 bond |
| Owner capture | `goal_text` immutable; owner may manage hosts only (v1) |
| Integrator ignore | Soft enforce by design; reference subject + integration guide |
| LLM variance | Parse fail → REJECTED; no default IMPROVED |

## Lifecycle

```text
DEPLOY
  owner, goal_text (immutable), initial genome, signal config
    ↓
ALLOW_HOST (owner)
    ↓
EVOLVE (anyone, after cooldown)
  fetch signal → propose genome + fitness
  consensus: IMPROVED | REJECTED
    ↓
IMPROVED → write genome, last_fitness, generation++
REJECTED → no state change
    ↓
SUBJECT contracts read genome / allows() before privileged actions
```

## Core API (v1)

| Method | Who | Role |
|--------|-----|------|
| `allow_host` / `disallow_host` | Owner | Signal hygiene |
| `evolve` | Anyone (post-cooldown) | Propose + consensus fitness gate |
| `get_genome` / `get_goal` / `get_generation` / `get_last_fitness` | View | Read state |
| `allows` or threshold getter | View | Integrator surface |
| `is_host_allowed` | View | Debug |

Exact method signatures freeze in Step 2 before any deploy.

## Consensus rules (v1)

- Labels: `IMPROVED` | `REJECTED` only (no soft “maybe”)
- Leader + validators use comparative principle: equivalent iff `decision` identical
- Note / reasoning non-binding
- IMPROVED requires parsed fitness strictly greater than `last_fitness` and goal-consistent judgment on signal
- Otherwise REJECTED

## Integration model

Soft enforcement (same class as many GenLayer primitives):

```text
genome = fitform.view().get_genome()
# or
if not fitform.view().allows("withdraw"):
    revert
```

---

### v1 vs v2

```markdown
## v1 vs v2

| v1 (ship) | v2 (designed, not required to start) |
|-----------|--------------------------------------|
| Single allowlisted signal URL | Multi-signal / quorum |
| Cooldown only | Evolve bond / slash path |
| Same-contract genome update | Optional IMPROVED-only child lineage |
| Owner host admin | Narrower governance / timelock on big jumps |
| Studionet E2E | Audit + external integrator |
```

## Limits (always document)

- Soft enforce: non-calling contracts ignore FitForm
- Genome is bounded; not arbitrary code evolution
- Signal quality depends on allowlisted sources
- Studionet / test deployments are not a production SLA
- LLM judgment is point-in-time under closed labels
- Mainnet production requires audit, parameters, and real integrators beyond this design

## Success criteria (before any “done”)

1. Live IMPROVED path changes genome and generation
2. Live REJECTED path leaves genome unchanged
3. Subject gated action differs pre/post IMPROVED
4. Unauthorized host / empty signal cannot IMPROVED
5. README vs-official table + limits visible

