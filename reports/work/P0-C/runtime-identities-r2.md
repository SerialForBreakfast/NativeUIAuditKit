# Corrected capture runtime identities

Observed 2026-09-22 UTC, before corpus completion. All paths relative to repository.

| Artifact | SHA-256 |
|---|---|
| `.build/debug/NativeUIDatasetGenerator` | `9a6bac35b1d7b78174b4cfde0247db222b84de1ff70c7bb19024005dbfaa6e36` |
| `GeneratorRunner.app/GeneratorRunner` | `54088c45a4281f55528bd6440ad8f4d1c669fa7d05a0f94ee589ae2566473e7e` |
| `GeneratorRunner.app/GeneratorRunner.debug.dylib` | `bdc2b30f3adfe449e1ac2722ee6769e83ffcaccf37b8be1e591e26f3b032b256` |
| `GeneratorRunner.app/PlugIns/GeneratorRunnerTests.xctest/GeneratorRunnerTests` | `dd30811512717d760d095f6b52a92f76a68c73144c17829c26c2a4b3117d8471` |

App artifact root:
`.build/NativeUIDatasetGenerator/DerivedData/Build/Products/Debug-iphonesimulator/`.
See source hash listing and reconstruction configuration for source/runtime identity.

Owned orchestrator PID at launch: 76364; app PID observed during capture: 76543.
These are historical observations, not authorization to signal reused PIDs.
Staging app-container UUID: `0FB6BE2F-241F-44F9-8F38-24FEF9884C4D` under the exact
authorized simulator's `data/Containers/Data/Application/` tree. Never use another
simulator or infer ownership from the bundle name alone.
