# FitForm — Design

## Thesis

FitForm is a GenLayer Intelligent Contract on the **Lifeform** track:

> A self-evolving contract that mutates a **bounded genome** and **selects** under fitness pressure and a dispute window before new rules go live — not free-form source-code mutation.

Foundation-style organisms mutate freely. FitForm mutates **and selects**.

## Track fit

Official idea: *Lifeform — a self-evolving contract that rewrites itself on a loop.*

- “Itself” = sealed goal + live genome (`rule_mode`, `threshold_milli`, `rule_note`)
- “On a loop” = permissionless `recheck` and `propose_evolve` (no admin keeper, no in-contract auto-queue)
- No human vote required for evolution

## Versus Foundation Living Organism

| | Foundation Living Organism | FitForm |
|--|----------------------------|---------|
| What evolves | Full contract source code | Bounded genome (rule_mode + threshold) |
| Selection | Structure checks only | Fitness + PENDING dispute + COMMIT |
| Deployment | Child contracts via deploy_contract | Same contract; live genome updates on COMMIT |
| Loop | Permissionless evolve | Permissionless recheck + propose + challenge + finalize |
| Failure | Broken child; parent intact | REJECTED / REVERT / EXTINCT |

## Lifecycle

propose_evolve
  → REJECTED  (no pending; live unchanged)
  → PENDING   (staged genome; allows() uses LIVE only)

challenge (while window open)
  → REVERT    (clear pending only; live unchanged)
  → UPHOLD    (pending remains)

finalize_evolve (after challenge window)
  → COMMIT    (live = pending; generation++; fitness; parent hash; history)

recheck
  → STABLE | DRIFT  (no silent write; anyone may propose after)

allows(action) reads LIVE genome only

## Genome

Live genes (deterministic allows):

- `rule_mode`: CLOSED | OWNER_ONLY | OPEN
- `threshold_milli`: 0–1000
- `rule_note`: rationale string (stored; does not gate allows)

allows("withdraw"):

- CLOSED → false
- OWNER_ONLY → false for general subject demo callers (subject treats as restricted unless mode OPEN)
- OPEN → true only if threshold_milli < 700

Subject demo must show CLOSED (or restricted) then OPEN after a COMMIT that sets rule_mode OPEN and threshold_milli under 700.

## Fitness and DRIFT

- `committed_fitness_milli` updated on COMMIT
- recheck fetches allowlisted HTTPS signal and scores live_fitness under sealed goal
- DRIFT if live_fitness + 50 < committed_fitness
- otherwise STABLE
- propose prompt includes recent history entries

## Lineage

On COMMIT:

- generation increments by 1
- parent_genome_hash set from previous live genome fingerprint
- history appends one JSON record (mode, threshold, fitness, note)

## EXTINCT

- failed_propose_count increments on REJECTED propose
- resets to 0 on COMMIT
- if failed_propose_count >= 5 → extinct = true
- if extinct: allows always false; propose, challenge, and finalize revert

## Consensus

Closed labels only. Comparative equivalence on decision field.

- propose: REJECTED | PENDING
- challenge: REVERT | UPHOLD

## Integration

Soft enforce:

if not fitform.view().allows("withdraw"):
    revert

Subject must prove restricted behavior then OPEN + act ok after an opening COMMIT.

## Non-goals

- Full Python source mutation or deploy_contract children
- In-contract auto-queue of propose from recheck
- Multi-sig evolution council
- Challenge bond (cooldown and gas only for this ship)
- Internal on-chain usage metrics as fitness
- HaltGate-style exploit halt

## Limits

- Soft enforce; contracts must call allows
- Studionet is not a production SLA
- LLM judgment is point-in-time under closed labels
- Permissionless loop needs external callers

## Success criteria

1. REJECTED propose leaves live genome unchanged
2. PENDING does not change allows until COMMIT
3. REVERT clears pending only
4. COMMIT updates generation, fitness, history; allows can flip to OPEN
5. recheck returns STABLE or DRIFT; unauthorized host and cooldown revert
6. Subject restricted then OPEN with act ok after opening COMMIT
7. README states mutation + selection vs Foundation free mutation

