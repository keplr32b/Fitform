# FitForm — Studionet E2E

## Instances

| Role | Address |
|------|---------|
| FitForm REJECTED demo | [0x239C2a2ecBE5fC85Dccb245255856f98F9e1702A](https://explorer-studio.genlayer.com/address/0x239C2a2ecBE5fC85Dccb245255856f98F9e1702A) |
| FitForm IMPROVED | [0xC385015C5d5D4E501117e479036d7362E8aE4d42](https://explorer-studio.genlayer.com/address/0xC385015C5d5D4E501117e479036d7362E8aE4d42) |
| ExampleSubject | [0x9344A6aE69fD53FBBBbaD075898E93Bb9EDee294](https://explorer-studio.genlayer.com/address/0x9344A6aE69fD53FBBBbaD075898E93Bb9EDee294) |

## REJECTED path (goal mismatched to withdraw-safety vs docs)

| Step | Result |
|------|--------|
| Deploy | [0xfb34d23ddea213b315ecb5a9c538c69f703814b0cfd5bda0b58efaff2cb539d2](https://explorer-studio.genlayer.com/tx/0xfb34d23ddea213b315ecb5a9c538c69f703814b0cfd5bda0b58efaff2cb539d2) |
| allow_host docs.genlayer.com | ok |
| evolve | **REJECTED** — [0x4c003110da31ec5f0eb36f89ea6c5a3e8e9e4db620657ea0918a310c5ce772da](https://explorer-studio.genlayer.com/tx/0x4c003110da31ec5f0eb36f89ea6c5a3e8e9e4db620657ea0918a310c5ce772da) |
| generation / fitness | remain 0 |

## IMPROVED path (goal aligned to official docs signal)

| Step | Result |
|------|--------|
| Deploy | [0xe2d375ae3df84dabd5dfec775aac655beac6308d2f24274355305f74a37e7133](https://explorer-studio.genlayer.com/tx/0xe2d375ae3df84dabd5dfec775aac655beac6308d2f24274355305f74a37e7133) |
| allow_host docs.genlayer.com | ok |
| evolve | **IMPROVED** — [0x79ed24d7af03d799dcd91a6a5583cb20a4ab84646ae5ef56617821cd6a0dadbc](https://explorer-studio.genlayer.com/tx/0x79ed24d7af03d799dcd91a6a5583cb20a4ab84646ae5ef56617821cd6a0dadbc) |
| generation | **1** |
| last_fitness | **870** |
| genome | rule_text updated; threshold_milli 780 |

## Subject integration

| Step | Result |
|------|--------|
| Deploy subject with FitForm IMPROVED | [0x278373c0c66612983b1b1ce021217a6b7a46539d5a8d8a09aaec2d9f9bb204b2](https://explorer-studio.genlayer.com/tx/0x278373c0c66612983b1b1ce021217a6b7a46539d5a8d8a09aaec2d9f9bb204b2) |
| status | **RESTRICTED** (threshold 780 not under 700) |
| act | ERROR `action not allowed by FitForm` — [0x0de8076614727d43e449fedb4b3280e6c6122097335fb03e4d3d594ca8f879a8](https://explorer-studio.genlayer.com/tx/0x0de8076614727d43e449fedb4b3280e6c6122097335fb03e4d3d594ca8f879a8) |
| get_acts | 0 |

## Design checks

- IMPROVED only when fitness rises under sealed goal + signal
- REJECTED leaves genome unchanged
- Soft enforce via `allows` + subject `view()` call
- Not full-source Living Organism factory