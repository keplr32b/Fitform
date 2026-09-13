# FitForm — Studionet E2E

## Contracts

| Role | Address |
|------|---------|
| FitForm | [0xf34d61dce2561A19a8691D966010F0B0C1377286](https://explorer-studio.genlayer.com/address/0xf34d61dce2561A19a8691D966010F0B0C1377286) |
| ExampleSubject | [0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC](https://explorer-studio.genlayer.com/address/0x77677DA6ebd88c9a5DEAa19aCF5025E10e427CfC) |

## Path: CLOSED → PENDING → COMMIT → OPEN

| Step | Result | Tx / note |
|------|--------|-----------|
| Deploy FitForm | SUCCESS | [0x3cf5a871…](https://explorer-studio.genlayer.com/tx/0x3cf5a87153603c17ff4d560d6e5daf6e2e063101f9b734825aaca3aa24e3e3cf) |
| allow_host docs.genlayer.com | ok | host only (not full URL) |
| allows(withdraw) initial | false | CLOSED |
| propose_evolve | **PENDING** OPEN/550/fitness 850 | [0xd41edc97…](https://explorer-studio.genlayer.com/tx/0xd41edc97485144fca8a41dbc43f74e2c27897ddb8f43f3add12c1b66dc6721db) |
| allows while pending | false | live genome unchanged |
| challenge after window | revert challenge window closed | window enforcement |
| finalize_evolve | **COMMIT** | generation 1 |
| get_genome | OPEN, 550, fitness 850, parent CLOSED\|800\|… | |
| allows(withdraw) | **true** | |
| Subject deploy | SUCCESS | [0x1d2e1ebc…](https://explorer-studio.genlayer.com/tx/0x1d2e1ebcd4d58fe19cbc4b87aecad6158d9e67f3fe9a77233668093144926147) |
| status / act / get_acts | OPEN / ok / 1 | |

## Design checks

- Mutation + selection (fitness gate + dispute window)
- Pending does not change allows
- COMMIT updates lineage (parent_genome_hash + history)
- Not Foundation source-factory lifeform