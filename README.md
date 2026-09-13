# FitForm

**Mutation + selection** for GenLayer (Lifeform track).

A sealed goal plus a bounded genome (`rule_mode`, `threshold_milli`). Anyone may `propose_evolve`. Validators score an allowlisted HTTPS signal under comparative consensus. Only **PENDING** stages a candidate; live `allows()` stays on the committed genome until **finalize** after the challenge window. **COMMIT** updates generation, fitness, parent hash, and history.

> Track: *A self-evolving contract that rewrites itself on a loop.*

FitForm rewrites **rules**, not arbitrary contract source code. Foundation-style organisms mutate freely; FitForm mutates **and selects**.

## Versus Foundation Living Organism

| | Foundation Living Organism | FitForm |
|--|----------------------------|---------|
| What evolves | Full contract source code | Bounded genome (rule_mode + threshold) |
| Selection | Structure checks only | Fitness + PENDING + challenge window + COMMIT |
| Deployment | Child contracts via deploy_contract | Same contract; live genome on COMMIT |
| Loop | Permissionless evolve | Permissionless recheck + propose + finalize |
| Failure | Broken child; parent intact | REJECTED / REVERT / window enforcement |

## Live Studionet

| Role | Address |
|------|---------|
| FitForm | [0xf34d61dce2561A19a8691D966010F0B0C1377286](https://explorer-studio.genlayer.com/address/0xf34d61dce2561A19a8691D966010F0B0C1377286) |
| ExampleSubject | [0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC](https://explorer-studio.genlayer.com/address/0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC) |

Proven on-chain:

- CLOSED → PENDING (staged OPEN) → COMMIT → `allows(withdraw)=true` → subject `act` ok
- Live `allows` stays false while PENDING
- UPHOLD + further COMMIT (generation lineage)
- Challenge window closed enforcement
- `recheck` → STABLE
- Parent genome hash + history on COMMIT

Full receipts: [verification/studionet-e2e.md](verification/studionet-e2e.md)

## Design

[docs/DESIGN.md](docs/DESIGN.md)

## Core flow

```text
propose_evolve → REJECTED | PENDING
challenge (while open) → REVERT | UPHOLD
finalize_evolve (after window) → COMMIT
recheck → STABLE | DRIFT
allows() reads LIVE genome only
```text

## Non-goals

- Full Python source mutation or deploy_contract children
- In-contract auto-queue propose from recheck
- Multi-sig evolution council
- Challenge bond (cooldown is from last propose; 300s challenge window usually exceeds it)

## Limits

- Soft enforce: integrators must call allows
- Studionet is not a production SLA
- LLM judgment is point-in-time under closed labels
- Permissionless loop needs external callers

## License

MIT