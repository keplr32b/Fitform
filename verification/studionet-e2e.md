# FitForm - Studionet E2E

## Contracts (v1 baseline)

| Role | Address |
|------|---------|
| FitForm | [0xf34d61dce2561A19a8691D966010F0B0C1377286](https://explorer-studio.genlayer.com/address/0xf34d61dce2561A19a8691D966010F0B0C1377286) |
| ExampleSubject | [0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC](https://explorer-studio.genlayer.com/address/0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC) |

## Deploy (v1)

| Step | Result |
|------|--------|
| FitForm deploy | [0x3cf5a87153603c17ff4d560d6e5daf6e2e063101f9b734825aaca3aa24e3e3cf](https://explorer-studio.genlayer.com/tx/0x3cf5a87153603c17ff4d560d6e5daf6e2e063101f9b734825aaca3aa24e3e3cf) |
| Constructor | goal=docs policy, signal=https://docs.genlayer.com, rule_mode=CLOSED, threshold=800 |
| allow_host | `docs.genlayer.com` (host only, not full URL) |

## Path A - First selection (CLOSED → OPEN)

| Step | Result | Tx / note |
|------|--------|-----------|
| allows(withdraw) | false | CLOSED |
| propose_evolve | PENDING (OPEN, thr 550, fitness 850) | [0xd41edc97485144fca8a41dbc43f74e2c27897ddb8f43f3add12c1b66dc6721db](https://explorer-studio.genlayer.com/tx/0xd41edc97485144fca8a41dbc43f74e2c27897ddb8f43f3add12c1b66dc6721db) |
| allows while pending | false | live unchanged |
| challenge after window | rollback: challenge window closed | window enforcement |
| finalize_evolve | COMMIT | generation 1, fitness 850 |
| get_genome | OPEN, 550, parent CLOSED\|800\|Initial closed genome | |
| allows(withdraw) | true | OPEN && thr < 700 |

## Path B - Subject integration

| Step | Result |
|------|--------|
| Subject deploy | [0x1d2e1ebcd4d58fe19cbc4b87aecad6158d9e67f3fe9a77233668093144926147](https://explorer-studio.genlayer.com/tx/0x1d2e1ebcd4d58fe19cbc4b87aecad6158d9e67f3fe9a77233668093144926147) |
| status | OPEN |
| act | ok |
| get_acts | 1 |

## Path C - UPHOLD + second COMMIT

| Step | Result |
|------|--------|
| propose_evolve | PENDING (fitness 925) |
| challenge | UPHOLD |
| finalize_evolve | COMMIT |
| generation | 2 |
| committed_fitness | 925 |
| parent_genome_hash | OPEN\|550\|… |

## Path D - Recheck + further COMMITs

| Step | Result | Tx |
|------|--------|-----|
| recheck | STABLE | [0xd65a3c44b412403a5987cae32e87a83528afdb1488c0c521da2b98c96b1b9650](https://explorer-studio.genlayer.com/tx/0xd65a3c44b412403a5987cae32e87a83528afdb1488c0c521da2b98c96b1b9650) |
| finalize (later pending) | COMMIT | [0x1d536dbad6e43332ad77d2211e095858297d4162e06b1635dd9d3567e965bbac](https://explorer-studio.genlayer.com/tx/0x1d536dbad6e43332ad77d2211e095858297d4162e06b1635dd9d3567e965bbac) |

---

## Consensus-fix deploy (resubmit)

**Rule:** `propose_evolve` comparative consensus agrees only on `decision` (PENDING | REJECTED). On PENDING, `rule_mode`, `threshold_milli`, and `fitness_milli` are derived deterministically (OPEN / 550 / live_fit+100), not from unbound leader LLM fields.

| Item | Value |
|------|--------|
| FitForm | [0xF5ca9090C3c706b7d36187e82AAB183727BfD147](https://explorer-studio.genlayer.com/address/0xF5ca9090C3c706b7d36187e82AAB183727BfD147) |
| Deploy | [0x1de7ae7519568800306cead87254538c92a5a7a150341c5ac9df50954ec3c48f](https://explorer-studio.genlayer.com/tx/0x1de7ae7519568800306cead87254538c92a5a7a150341c5ac9df50954ec3c48f) |

| Step | Result | Tx |
|------|--------|-----|
| allow_host docs.genlayer.com | ok | [0x79c8e3269730436541aeaa3a64456095f263e21abd625b6675e3bc39598946fd](https://explorer-studio.genlayer.com/tx/0x79c8e3269730436541aeaa3a64456095f263e21abd625b6675e3bc39598946fd) |
| propose_evolve | PENDING · is_pending true · OPEN/550/fitness 100 | [0x2bfa4c2c157766909e2c95053576e84ba070b8b5006673cd94545a2e7c1fa3ef](https://explorer-studio.genlayer.com/tx/0x2bfa4c2c157766909e2c95053576e84ba070b8b5006673cd94545a2e7c1fa3ef) |
| finalize_evolve | COMMIT · generation 1 | [0x88b2b61e9217b158d8cc84d3ca3afeea274fcf2c2471ef0d70d6a52240bf3e81](https://explorer-studio.genlayer.com/tx/0x88b2b61e9217b158d8cc84d3ca3afeea274fcf2c2471ef0d70d6a52240bf3e81) |
| allows(withdraw) | true | view |

---

## Notes

- Cooldown is measured from last `propose_evolve`, not finalize. After a 300s challenge window the cooldown has usually already elapsed; prove cooldown via rapid proposes only when not pending (e.g. after REJECTED).
- allow_host must be hostname (`docs.genlayer.com`), not `https://...`.
- Pending proposals do not change `allows` until COMMIT.
- Resubmit build: decision-only consensus; consequential genome fields deterministic on PENDING.