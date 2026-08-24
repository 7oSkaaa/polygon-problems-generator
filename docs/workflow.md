# Workflow

How this repo is meant to be used, including how to fix a problem after local verify or Polygon complains.

## Intended loop

```
idea → generate locally → originality → ./verify.sh → polyup → Polygon package verify
                ↑                         |                    |
                └──── prompt a targeted fix ←──────────────────┘
```

1. **Create the problem locally** with `/generate-problem` (or the orchestrator). All files land in `problems/<name>/`.
2. **Originality** — `python -m polyup originality <name>` searches [yuantiji.ac](http://yuantiji.ac/en/). Copies and near-duplicates **block** the pipeline except for Ace and Div2-A.
3. **Local verify** — `./verify.sh problems/<name>` compiles with `-Wall -Wextra -Werror`, runs validator tests, samples, ACC / Java / `acc_alt`, WA rejection, and ACC-vs-brute stress. See [verify.md](verify.md).
4. **Upload** — `python -m polyup <name>` pushes to Polygon and builds the package with `verify=true` (invocations on the server). That is the official check.
5. **If something fails**, do **not** regenerate the whole problem. Prompt a **single-component fix** (below) with the log pasted in.

Polygon is for: statement PDF, invocations on the full testset, time-limit calibration, and warnings the local harness cannot see. It is not the first debugger.

## How to prompt a fix

Name the folder, the file, and paste the failure. Keep the rest of the problem unchanged.

**Local verify failed**

```
Fix problems/<name>/solutions/acc.cpp.
verify.sh failed with:
<paste the failing section>
Keep validator, generator, and the statement unchanged.
```

**Polygon warning / invocation**

```
Fix problems/<name>/validator.cpp.
Polygon says:
<paste the warning or invocation log>
Regenerate only the validator. Then I will re-run ./verify.sh and polyup.
```

**Statement / tutorial wording**

```
Revise problems/<name>/statement/statement.tex:
- <bullet list of issues>
Keep Input/Output constraints identical. Do not rename variables.
```

**Originality blocked**

```
yuantiji flagged this as similar to <url> (cos=...).
Propose a different task with the same difficulty, not a restatement of that problem.
```

You can also run `/fix-component` if that command is available.

The orchestrator should spawn only the matching sub-agent (`validator-agent`, `solutions-agent`, …) with the existing file + the error log as feedback.

## verify.sh vs Polyman vs Polygon

| Tool | What it is |
|---|---|
| **`./verify.sh`** | Lightweight **pre-upload** harness in this repo. Compiles sources, runs validator tests and a slice of generated tests, cross-checks solutions, stresses ACC vs brute. Does **not** execute Polygon FreeMarker scripts as Polygon would, does **not** download a problem, does **not** replace invocations. |
| **Polyman** | A separate local Polygon-like environment: pull a problem, generate tests the way Polygon does, run invocations locally. Heavier, closer to the server. Use it if you want a full local clone of Polygon's test runner. |
| **`python -m polyup` + package verify** | Uploads the folder and asks Polygon to **build the package with verification**. This is the official compile + invocations pass. `--no-verify` skips that build check. |

Use `verify.sh` until it is green, then Polyman *or* Polygon — not Polygon as the only test runner.

## Originality (yuantiji)

```bash
python -m polyup originality <name>
# or via verify.sh (default on)
./verify.sh problems/<name> --skip-originality   # offline
```

The public API is `POST https://yuantiji.ac/api/search` ([is-my-problem-new](https://github.com/fjzzq2002/is-my-problem-new)). Thresholds: cosine ≥ 0.90 copy, ≥ 0.85 similar (override with `YUANTIJI_COPY` / `YUANTIJI_SIMILAR`). Ace / Div2-A are advisory only.
