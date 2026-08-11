# Config Reference Overview

Three notes in this folder share near-identical titles ("Config Reference" / "`config.py` Reference" / "Configuration Reference") but are **genuinely distinct documents** written in different working sessions, not duplicates — confirmed by diff during the Phase-1 dedup pass (see [[00_Inbox/Dedup_Map]]). This note disambiguates which is which.

| Note | Source | Angle |
|---|---|---|
| [[Config_Reference]] | `docs/config_reference.md` | Dataset-root and path configuration for the visibility analysis run — where things live on disk |
| [[KRadar_configpy_Reference]] | `docs/kradar_config.md` | Direct reference to `kradar_visibility/config.py` as a module — constants as they appear in code |
| [[K-Radar_Configuration_Reference]] | `docs/kradar_config_reference.md` | Broader configuration reference, `src/kradar_visibility/config.py` framed for a reader without the file open |

For the authoritative, currently-accurate constant values (FOV angles, LiDAR channel counts, camera weights, output schema), prefer [[04_Design/API_Contracts]] and [[04_Design/Output_Schema]] — those were synthesized directly from `api_contracts.md`/`architecture.md` during Phase 2 and cross-checked against the pipeline's actual `config.py`. The three notes above are kept as historical working documents, not re-verified against current code.

## Source

- `docs/config_reference.md`, `docs/kradar_config.md`, `docs/kradar_config_reference.md`
- `docs/vAIlt/00_Inbox/Dedup_Map.md` (false-positive check that ruled these out as duplicates)
