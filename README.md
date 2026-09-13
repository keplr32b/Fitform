# FitForm

Fitness-gated **self-evolving rules** for GenLayer (Lifeform track).

A sealed goal plus a bounded genome (rule text / parameters). Anyone may call `evolve`. Validators fetch an allowlisted public signal and reach comparative consensus on a closed label: **IMPROVED** or **REJECTED**. The genome updates only on **IMPROVED** — when fitness is strictly better under the sealed goal. Integrator contracts read the genome (or `allows`) before privileged actions.

> Track idea: *A self-evolving contract that rewrites itself on a loop.*

FitForm rewrites **its rules**, not arbitrary contract source code.

## Versus Foundation Living Organism

| | Foundation Living Organism | FitForm |
|--|----------------------------|---------|
| What evolves | Full contract source code | Bounded genome (params / rule text) |
| Accept rule | Structural preserve | **IMPROVED** fitness vs sealed goal + signal |
| Deployment | Always `deploy_contract` child | Same-contract update (v1) |
| Success signal | Meaningful mutation + structure checks | Measurable fitness increase |
| Failure | Broken child; parent intact | Reject; genome unchanged |

FitForm is intentionally **stricter** on accept conditions and **narrower** on what may change.

## Live Studionet

| Role | Address |
|------|---------|
| FitForm | [0xf34d61dce2561A19a8691D966010F0B0C1377286](https://explorer-studio.genlayer.com/address/0xf34d61dce2561A19a8691D966010F0B0C1377286) |
| ExampleSubject | [0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC](https://explorer-studio.genlayer.com/address/0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC) |

Proven: CLOSED → PENDING (staged OPEN) → COMMIT → allows true → subject act ok. Generation 1, fitness 850, parent hash retained.

Receipts: [verification/studionet-e2e.md](verification/studionet-e2e.md)

Proven on-chain: REJECTED leaves generation at 0; IMPROVED sets generation 1 and fitness 870; subject status RESTRICTED and `act` reverts with `action not allowed by FitForm`.

Full receipts: [verification/studionet-e2e.md](verification/studionet-e2e.md)

## Design

[docs/DESIGN.md](docs/DESIGN.md)

## Core idea

```text
goal (immutable) + genome (mutable)
        ↓
evolve() → signal + consensus
        ↓
IMPROVED → genome / generation update
REJECTED → no change
        ↓
subjects read genome before acting
```text

## Non-goals
- Full Python source mutation as identity
- Forcing non-integrating contracts
- Stablecoin / emergency halt product
- Owner silently rewriting goal or fake fitness
- Mainnet production SLA without audit and real integrators

## Limits

- Soft enforce: contracts must call FitForm views
- Genome is bounded; not unbounded code evolution
- Signal quality depends on allowlisted HTTPS sources
- LLM judgment is point-in-time under closed labels
- Testnet / Studionet deployments are not a production SLA

## License

MIT