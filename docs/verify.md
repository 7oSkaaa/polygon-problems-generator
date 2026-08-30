# verify.sh

Local pre-upload checks for a problem folder. This is **not** Polyman and **not** Polygon's package builder.

```bash
./verify.sh problems/<name> [--stress N] [--keep] [--skip-originality] [--skip-stress]
```

| Flag | Meaning |
|---|---|
| `--stress N` | ACC vs brute iterations (default 1000) |
| `--keep` | Keep `problems/<name>/.build` and `.tests` after the run |
| `--skip-originality` | Do not call yuantiji.ac |
| `--skip-stress` | Skip ACC vs brute |

What it does:

0. Static checks (no `#pragma GCC optimize`, legal file names)
1. Originality search (`python -m polyup originality <name>`) — blocks similar/copy except Ace / Div2-A
2. Compile validator, generator, checker, interactor, solutions with `g++ -std=c++17 -Wall -Wextra -Werror`, and Java ACC with JDK 21 (`./scripts/setup-deps.sh` if `javac` is missing; macOS stub `javac` does not count)
3. Run generator script lines from the FreeMarker comment and **fail if two tests (or a test and a sample) are equal**
4. Run `validator_tests/` (`valid*` must pass, others must fail)
5. Validate samples + a handful of generator outputs
6. Run `acc.cpp`; compare samples; Java and `acc_alt.cpp` vs checker
7. Confirm `wa.cpp` is rejected on at least one test
8. Stress `acc` vs `brute` on small random tests (non-interactive)

After a green run:

```bash
python -m polyup <name>
```

Polygon still builds the package (`verify=true` unless `--no-verify`) and runs full invocations.

Interactive problems skip checker-vs-WA and ACC-vs-brute (the interactor issues WA on query limit; tag `brute.cpp` as Wrong Answer).

## Compared to Polyman

Polyman reproduces Polygon's generate-tests + invocations loop locally. `verify.sh` is a fast sanity net so you do not upload code that does not compile, a validator that rejects samples, or an ACC that disagrees with the brute. It does not interpret FreeMarker scripts the way Polygon does.

See also [workflow.md](workflow.md).
