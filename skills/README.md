# Idea skills — factor inspiration and hypothesis design

A small, portable skill pack for the **idea layer** only: finding economically
meaningful patterns, turning them into falsifiable hypotheses, and emitting them
in the exact JSON contract used by the project's Agent 2 ideation interface.

The pack deliberately stops at the hypothesis. Implementation, parameter search
and any performance assessment belong to the existing `factorlab` pipeline; no
skill here asks an agent to run code, compute performance or judge results.

## Skills

| skill | use it when | output |
|---|---|---|
| `factor-idea-scout` | you need fresh mechanism-first factor ideas from a data contract or EDA summary | 4-8 idea JSONs |
| `anomaly-taxonomy` | you want documented market anomalies organised by mechanism and available fields | mechanism shortlist + idea JSONs |
| `paper-to-hypothesis` | you have a paper/report finding and want a testable cross-sectional hypothesis | 1-3 idea JSONs + evidence notes |
| `event-theme-radar` | a macro event, news theme or regime shift should become factor ideas | 3-6 idea JSONs mapped to fields |
| `hypothesis-formalizer` | a rough thesis must become a contract-valid idea record | one validated idea JSON |
| `idea-diversity-planner` | you are planning a batch and must avoid clustering / repetition | batch coverage plan + idea JSONs |

Shared references (read before writing any idea):

* `_shared/references/idea_contract.md` — the 15-field idea contract and its hard rules
* `_shared/references/panel_fields.md` — the available datasets and field vocabulary
* `_shared/references/anomaly_catalog.md` — mechanism catalogue with fields, direction, horizon and failure modes

## Install

Copy the pack into the skills directory used by your agent runtime, or keep it
in the repository and point the agent at `skills/`:

```powershell
python skills/install.py --dest "$env:USERPROFILE\.claude\skills"
python skills/install.py --dest "$env:USERPROFILE\.dsh\skills"
```

The installer copies each skill to `<dest>/<skill-name>/SKILL.md` and puts the
shared references next to it in `<dest>/<skill-name>/references/`. It is
idempotent; `--dry-run` prints the plan without writing anything.

Validate the pack (front matter, idea contract, boundary rules):

```powershell
python skills/validate.py
```

## Boundary rules (enforced by `validate.py`)

1. Skills describe **mechanisms and hypotheses**, never results.
2. `mechanism` and `signal_concept` must be prose: no formulas, no code fences.
3. Every idea names at least one applicability limit and one failure mode.
4. Every idea lists the fields it needs from the available vocabulary and states
   its expected direction and horizon.
5. Nothing in this pack asks an agent to run code, compute statistics or rank
   candidates; that is the job of the existing pipeline.

## Layout

```
skills/
  README.md
  validate.py
  install.py
  _shared/references/idea_contract.md
  _shared/references/panel_fields.md
  _shared/references/anomaly_catalog.md
  factor-idea-scout/SKILL.md
  anomaly-taxonomy/SKILL.md
  paper-to-hypothesis/SKILL.md
  event-theme-radar/SKILL.md
  hypothesis-formalizer/SKILL.md
  idea-diversity-planner/SKILL.md
  examples/idea_batch.json
```
