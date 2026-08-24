#!/bin/bash
set -euo pipefail

# ── Local Polygon-style verify ───────────────────────────────────────────────
# Usage:
#   ./verify.sh problems/<name> [--stress N] [--keep] [--skip-originality] [--skip-stress]
#
# This is the local pre-upload harness. It is not Polyman and it is not
# Polygon's package builder. After this passes, upload with:
#   python -m polyup <name>
# Polygon's "build package (verify)" is still the official invocation check.
#
# Steps:
#   0. Static checks (pragma, file names)
#   1. Originality search via yuantiji.ac (skipped for Ace / Div2-A)
#   2. Compile validator, generator, solutions, checker with -Wall -Wextra -Werror
#   3. Run validator tests (valid_* / invalid_*)
#   4. Validate samples + generator tests
#   5. Run ACC, Java cross-check, checker sanity, WA rejection
#   6. Stress ACC vs brute (non-interactive)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
header() { echo -e "\n${BOLD}[$1]${NC}"; }

usage() {
    echo "Usage: ./verify.sh problems/<name> [--stress N] [--keep] [--skip-originality] [--skip-stress]"
    exit 1
}

PROBLEM_DIR=""
STRESS_COUNT=1000
KEEP=false
SKIP_ORIGINALITY=false
SKIP_STRESS=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --stress)
            STRESS_COUNT="${2:-}"; shift 2
            [[ -n "$STRESS_COUNT" ]] || usage
            ;;
        --keep) KEEP=true; shift ;;
        --skip-originality) SKIP_ORIGINALITY=true; shift ;;
        --skip-stress) SKIP_STRESS=true; shift ;;
        -h|--help) usage ;;
        *)
            if [[ -z "$PROBLEM_DIR" ]]; then
                PROBLEM_DIR="$1"; shift
            else
                usage
            fi
            ;;
    esac
done

[[ -n "$PROBLEM_DIR" ]] || usage
PROBLEM_DIR="${PROBLEM_DIR%/}"

if [[ ! -d "$PROBLEM_DIR" ]]; then
    echo "Error: $PROBLEM_DIR not found"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TESTLIB="$REPO_ROOT/testlib/testlib.h"
STANDARD_CHECKERS="$REPO_ROOT/testlib/checkers"
CXX="${CXX:-g++}"
CXXFLAGS="-std=c++17 -O2 -Wall -Wextra -Werror -I$(dirname "$TESTLIB") -I$HOME/.local/include"
BUILD="$PROBLEM_DIR/.build"
TESTS="$PROBLEM_DIR/.tests"
FAILURES=0
INTERACTIVE=false
[[ -f "$PROBLEM_DIR/interactor.cpp" ]] && INTERACTIVE=true

if command -v gtimeout &>/dev/null; then
    run_timed() { gtimeout "$@"; }
elif command -v timeout &>/dev/null 2>&1 && timeout --version &>/dev/null 2>&1; then
    run_timed() { timeout "$@"; }
else
    run_timed() { shift; "$@"; }
fi

cleanup() {
    if [[ "$KEEP" == true ]]; then
        echo -e "  ${YELLOW}→${NC} keeping $BUILD and $TESTS (--keep)"
        return
    fi
    rm -rf "$BUILD" "$TESTS"
}
trap cleanup EXIT

mkdir -p "$BUILD" "$TESTS"

echo -e "${BOLD}Verifying: ${PROBLEM_DIR}${NC}"
if [[ "$INTERACTIVE" == true ]]; then
    echo -e "  ${YELLOW}→${NC} interactive problem detected"
fi

# ── 0. Static checks ─────────────────────────────────────────────────────────

header "Static checks"

bad_pragma=0
for src in "$PROBLEM_DIR/solutions/"*.cpp "$PROBLEM_DIR/solutions/"*.java \
           "$PROBLEM_DIR/validator.cpp" "$PROBLEM_DIR/checker.cpp" \
           "$PROBLEM_DIR/interactor.cpp"; do
    [[ -f "$src" ]] || continue
    if grep -E '#pragma[[:space:]]+GCC[[:space:]]+optimize|#pragma[[:space:]]+clang[[:space:]]+optimize' "$src" >/dev/null 2>&1; then
        fail "compiler-optimization pragma in $(basename "$src")"
        bad_pragma=1
    fi
    base=$(basename "$src")
    if [[ "$base" =~ [^A-Za-z._] ]]; then
        fail "illegal character in file name $base (letters, '.', '_' only)"
    fi
done
[[ $bad_pragma -eq 0 ]] && pass "No optimization pragmas"
pass "File names checked"

# ── 1. Originality ───────────────────────────────────────────────────────────

header "Originality (yuantiji.ac)"

if [[ "$SKIP_ORIGINALITY" == true ]]; then
    warn "Skipped (--skip-originality)"
else
    if ( cd "$REPO_ROOT" && python3 -m polyup originality "$(basename "$PROBLEM_DIR")" ); then
        pass "Originality check passed (or advisory-only for Ace / Div2-A)"
    else
        status=$?
        if [[ $status -eq 1 ]]; then
            fail "Too similar to an existing problem — see originality.json"
        else
            warn "Originality search could not run (network?). Re-run or use --skip-originality"
        fi
    fi
fi

# ── 2. Checker ───────────────────────────────────────────────────────────────

header "Checker"

CHECKER_SRC="$PROBLEM_DIR/checker.cpp"
CUSTOM_CHECKER=false

if [[ -f "$CHECKER_SRC" ]]; then
    first_line=$(head -1 "$CHECKER_SRC")
    if [[ "$first_line" == "// Use standard checker:"* ]]; then
        CHECKER_NAME=$(echo "$first_line" | sed 's/.*: \([a-z0-9]*\).*/\1/')
        CHECKER_STANDARD_SRC="$STANDARD_CHECKERS/${CHECKER_NAME}.cpp"
        if [[ -f "$CHECKER_STANDARD_SRC" ]]; then
            $CXX $CXXFLAGS -o "$BUILD/checker" "$CHECKER_STANDARD_SRC"
            pass "Standard checker: $CHECKER_NAME"
        else
            fail "Standard checker '$CHECKER_NAME' not found in $STANDARD_CHECKERS"
        fi
    else
        CUSTOM_CHECKER=true
        if $CXX $CXXFLAGS -o "$BUILD/checker" "$CHECKER_SRC"; then
            pass "Custom checker compiled (-Werror)"
        else
            fail "Custom checker failed to compile"
        fi
    fi
else
    fail "No checker.cpp found"
fi

# ── 3. Validator / generator / interactor ────────────────────────────────────

header "Validator"

VALIDATOR_SRC="$PROBLEM_DIR/validator.cpp"
if [[ -f "$VALIDATOR_SRC" ]]; then
    if $CXX $CXXFLAGS -o "$BUILD/validator" "$VALIDATOR_SRC"; then
        pass "Compiled"
    else
        fail "validator.cpp failed to compile"
    fi
else
    fail "No validator.cpp found"
fi

header "Generator"

GEN_SRC=$(find "$PROBLEM_DIR/generators" -name "generator.cpp" 2>/dev/null | head -1)
if [[ -n "$GEN_SRC" ]]; then
    if $CXX $CXXFLAGS -o "$BUILD/gen" "$GEN_SRC"; then
        pass "Compiled"
    else
        fail "generator.cpp failed to compile"
    fi
else
    fail "No generator.cpp found"
fi

if [[ "$INTERACTIVE" == true ]]; then
    header "Interactor"
    if $CXX $CXXFLAGS -o "$BUILD/interactor" "$PROBLEM_DIR/interactor.cpp"; then
        pass "Compiled"
    else
        fail "interactor.cpp failed to compile"
    fi
fi

# ── 4. Solutions ─────────────────────────────────────────────────────────────

header "Solutions"

compile_solution() {
    local src="$1"
    local name
    name=$(basename "$src" .cpp)
    name=$(basename "$name" .java)
    local ext="${src##*.}"

    if [[ "$ext" == "cpp" ]]; then
        if $CXX $CXXFLAGS -o "$BUILD/$name" "$src"; then
            pass "$name.cpp"
        else
            fail "$name.cpp failed to compile"
        fi
    elif [[ "$ext" == "java" ]]; then
        local classname
        classname=$(basename "$src" .java)
        if command -v javac &>/dev/null; then
            if javac -Xlint:all -d "$BUILD" "$src"; then
                pass "$classname.java"
            else
                fail "$classname.java failed to compile"
            fi
        else
            warn "$classname.java skipped (javac not found)"
        fi
    fi
}

shopt -s nullglob
for src in "$PROBLEM_DIR/solutions/"*.cpp "$PROBLEM_DIR/solutions/"*.java; do
    compile_solution "$src"
done
shopt -u nullglob

if [[ ! -x "$BUILD/acc" ]]; then
    fail "acc binary not found"
fi
if [[ ! -f "$PROBLEM_DIR/solutions/acc_java.java" ]]; then
    warn "acc_java.java missing — checklist requires C++ and Java ACC"
fi
if [[ ! -f "$PROBLEM_DIR/solutions/acc_alt.cpp" ]]; then
    warn "acc_alt.cpp missing — checklist requires a second ACC with a different approach"
fi

# ── 5. Validator tests ───────────────────────────────────────────────────────

header "Validator tests"

VTEST_DIR="$PROBLEM_DIR/validator_tests"
if [[ -d "$VTEST_DIR" && -x "$BUILD/validator" ]]; then
    v_ok=0
    v_bad=0
    v_total=0
    for f in "$VTEST_DIR"/*; do
        [[ -f "$f" ]] || continue
        v_total=$((v_total + 1))
        name=$(basename "$f")
        if "$BUILD/validator" < "$f" >/dev/null 2>&1; then
            accepted=true
        else
            accepted=false
        fi
        if [[ "$name" == valid* ]]; then
            if [[ "$accepted" == true ]]; then
                v_ok=$((v_ok + 1))
            else
                v_bad=$((v_bad + 1))
                warn "expected VALID: $name"
            fi
        else
            if [[ "$accepted" == false ]]; then
                v_ok=$((v_ok + 1))
            else
                v_bad=$((v_bad + 1))
                warn "expected INVALID: $name"
            fi
        fi
    done
    if [[ $v_total -eq 0 ]]; then
        warn "validator_tests/ is empty"
    elif [[ $v_bad -eq 0 ]]; then
        pass "$v_ok/$v_total validator tests behaved as expected"
    else
        fail "$v_bad/$v_total validator tests mismatched"
    fi
else
    warn "No validator_tests/ — Polygon checklist requires validator tests"
fi

# ── 6. Samples + generated tests ─────────────────────────────────────────────

header "Test generation + validation"

test_idx=0
gen_fail=0
val_fail=0

copy_input() {
    local src="$1"
    test_idx=$((test_idx + 1))
    cp "$src" "$TESTS/test_${test_idx}.in"
    if [[ -x "$BUILD/validator" ]] && ! "$BUILD/validator" < "$TESTS/test_${test_idx}.in" >/dev/null 2>&1; then
        val_fail=$((val_fail + 1))
        [[ $val_fail -le 3 ]] && warn "Validator rejected $(basename "$src")"
    fi
}

if [[ -d "$PROBLEM_DIR/samples" ]]; then
    for inp in "$PROBLEM_DIR/samples/"*.in; do
        [[ -f "$inp" ]] || continue
        copy_input "$inp"
        out="${inp%.in}.out"
        if [[ -f "$out" ]]; then
            cp "$out" "$TESTS/test_${test_idx}.sample_out"
        fi
    done
fi

auto_stress_args() {
    local gen_src="$1"
    [[ -f "$gen_src" ]] || return
    grep -oE 'opt<int>\("([^"]+)",\s*([^)]+)\)' "$gen_src" | \
    sed -E 's/opt<int>\("([^"]+)",\s*([^)]+)\)/\1 \2/' | \
    while read -r name default_expr; do
        val=$(echo "$default_expr" | tr -d "'" | tr -d ' ')
        if ! [[ "$val" =~ ^-?[0-9]+$ ]]; then
            continue
        fi
        val=$((val))
        if (( val >= 1000000 )); then
            echo "-${name} 100"
        elif (( val >= 1000 )); then
            echo "-${name} 100"
        fi
    done | tr '\n' ' '
}

if [[ -f "$PROBLEM_DIR/stress.conf" ]]; then
    STRESS_GEN_ARGS=$(cat "$PROBLEM_DIR/stress.conf")
elif [[ -n "${STRESS_GEN_ARGS:-}" ]]; then
    :
elif [[ -n "$GEN_SRC" ]]; then
    STRESS_GEN_ARGS=$(auto_stress_args "$GEN_SRC")
fi
STRESS_GEN_ARGS="${STRESS_GEN_ARGS:-}"

if [[ -x "$BUILD/gen" && -x "$BUILD/validator" ]]; then
    EDGE_SEEDS=(1 2 3 4 5 6 7 8 9 10)
    for seed in "${EDGE_SEEDS[@]}"; do
        test_idx=$((test_idx + 1))
        if "$BUILD/gen" $STRESS_GEN_ARGS "$seed" > "$TESTS/test_${test_idx}.in" 2>/dev/null; then
            if ! "$BUILD/validator" < "$TESTS/test_${test_idx}.in" >/dev/null 2>&1; then
                val_fail=$((val_fail + 1))
                [[ $val_fail -le 3 ]] && warn "Validator rejected generated seed=$seed"
            fi
        else
            gen_fail=$((gen_fail + 1))
        fi
    done
fi

if [[ $test_idx -eq 0 ]]; then
    warn "No tests generated"
elif [[ $gen_fail -eq 0 && $val_fail -eq 0 ]]; then
    pass "Prepared $test_idx tests, all passed validation"
else
    [[ $val_fail -gt 0 ]] && fail "$val_fail/$test_idx tests rejected by validator"
    [[ $gen_fail -gt 0 ]] && fail "$gen_fail generated tests failed to write"
fi

# ── 7. ACC ───────────────────────────────────────────────────────────────────

header "ACC solution"

if [[ -x "$BUILD/acc" ]]; then
    acc_fail=0
    for input in "$TESTS"/test_*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        if ! run_timed 5 "$BUILD/acc" < "$input" > "$TESTS/${base}.ans" 2>/dev/null; then
            acc_fail=$((acc_fail + 1))
        fi
        sample_out="$TESTS/${base}.sample_out"
        if [[ -f "$sample_out" ]] && ! diff -q "$TESTS/${base}.ans" "$sample_out" >/dev/null 2>&1; then
            acc_fail=$((acc_fail + 1))
            warn "ACC disagrees with sample output on $base"
        fi
    done
    total=$(ls "$TESTS"/test_*.in 2>/dev/null | wc -l | tr -d ' ')
    if [[ $acc_fail -eq 0 ]]; then
        pass "Ran on $total tests"
    else
        fail "$acc_fail/$total tests failed, timed out, or missed a sample"
    fi
else
    fail "acc binary not found"
fi

# ── 8. Checker sanity ────────────────────────────────────────────────────────

header "Checker sanity (ACC vs ACC)"

if [[ "$INTERACTIVE" == true ]]; then
    warn "Skipped for interactive problems (interactor issues the verdict)"
elif [[ -x "$BUILD/checker" && -x "$BUILD/acc" ]]; then
    chk_fail=0
    for input in "$TESTS"/test_*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        ans="$TESTS/${base}.ans"
        [[ -f "$ans" ]] || continue
        if ! "$BUILD/checker" "$input" "$ans" "$ans" >/dev/null 2>&1; then
            chk_fail=$((chk_fail + 1))
            [[ $chk_fail -le 3 ]] && warn "Checker rejected ACC output on $base"
        fi
    done
    total=$(ls "$TESTS"/test_*.ans 2>/dev/null | wc -l | tr -d ' ')
    if [[ $chk_fail -eq 0 ]]; then
        pass "All $total tests accepted"
    else
        fail "$chk_fail/$total tests rejected by checker"
    fi
else
    warn "Skipped (missing checker or acc)"
fi

# ── 9. Extra ACC cross-check (Java + acc_alt) ────────────────────────────────

cross_check() {
    local label="$1"
    local runner="$2"
    header "$label"
    local failc=0 total=0
    for input in "$TESTS"/test_*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        ans="$TESTS/${base}.ans"
        [[ -f "$ans" ]] || continue
        total=$((total + 1))
        out="$TESTS/${base}.${label}.out"
        if eval "$runner" < "$input" > "$out" 2>/dev/null; then
            if [[ "$INTERACTIVE" != true ]] && [[ -x "$BUILD/checker" ]]; then
                if ! "$BUILD/checker" "$input" "$out" "$ans" >/dev/null 2>&1; then
                    failc=$((failc + 1))
                fi
            elif ! diff -q "$ans" "$out" >/dev/null 2>&1; then
                failc=$((failc + 1))
            fi
        else
            failc=$((failc + 1))
        fi
    done
    if [[ $total -eq 0 ]]; then
        warn "No tests"
    elif [[ $failc -eq 0 ]]; then
        pass "Matches C++ ACC on $total tests"
    else
        fail "$label differs on $failc/$total tests"
    fi
}

if [[ -f "$BUILD/acc_java.class" ]]; then
    cross_check "Java ACC" "run_timed 10 java -cp \"$BUILD\" acc_java"
else
    header "Java ACC"
    warn "Skipped (no acc_java.class)"
fi

if [[ -x "$BUILD/acc_alt" ]]; then
    cross_check "alt ACC" "run_timed 5 \"$BUILD/acc_alt\""
else
    header "alt ACC"
    warn "Skipped (no acc_alt)"
fi

# ── 10. WA rejection ─────────────────────────────────────────────────────────

header "WA solution rejection"

if [[ "$INTERACTIVE" == true ]]; then
    warn "Skipped for interactive (WA is issued by the interactor on bad queries)"
elif [[ -x "$BUILD/wa" && -x "$BUILD/checker" ]]; then
    wa_rejected=0
    wa_total=0
    for input in "$TESTS"/test_*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        ans="$TESTS/${base}.ans"
        [[ -f "$ans" ]] || continue
        wa_total=$((wa_total + 1))
        wa_out="$TESTS/${base}.wa_out"
        run_timed 5 "$BUILD/wa" < "$input" > "$wa_out" 2>/dev/null || true
        if ! "$BUILD/checker" "$input" "$wa_out" "$ans" >/dev/null 2>&1; then
            wa_rejected=$((wa_rejected + 1))
        fi
    done
    if [[ $wa_rejected -gt 0 ]]; then
        pass "Rejected on $wa_rejected/$wa_total tests"
    else
        fail "WA solution was never rejected — checker or WA solution may be wrong"
    fi
else
    warn "Skipped (missing wa or checker)"
fi

# ── 11. Stress ───────────────────────────────────────────────────────────────

header "Stress test (ACC vs Brute, $STRESS_COUNT iterations)"

if [[ -n "$STRESS_GEN_ARGS" ]]; then
    echo -e "  ${YELLOW}→${NC} stress args: $STRESS_GEN_ARGS"
fi

if [[ "$SKIP_STRESS" == true ]]; then
    warn "Skipped (--skip-stress)"
elif [[ "$INTERACTIVE" == true ]]; then
    warn "Skipped for interactive problems (brute is tagged WA, not TLE)"
elif [[ -x "$BUILD/acc" && -x "$BUILD/brute" && -x "$BUILD/gen" ]]; then
    mismatch=0
    for i in $(seq 1 "$STRESS_COUNT"); do
        "$BUILD/gen" $STRESS_GEN_ARGS "$i" > "$TESTS/_stress.in" 2>/dev/null
        run_timed 5 "$BUILD/acc" < "$TESTS/_stress.in" > "$TESTS/_stress.acc" 2>/dev/null
        run_timed 30 "$BUILD/brute" < "$TESTS/_stress.in" > "$TESTS/_stress.brute" 2>/dev/null || true
        if ! diff -q "$TESTS/_stress.acc" "$TESTS/_stress.brute" >/dev/null 2>&1; then
            mismatch=$((mismatch + 1))
            if [[ $mismatch -le 1 ]]; then
                echo ""
                warn "First mismatch on seed=$i:"
                echo "    Input:    $(head -3 "$TESTS/_stress.in" | tr '\n' ' ')"
                echo "    ACC:      $(cat "$TESTS/_stress.acc")"
                echo "    Brute:    $(cat "$TESTS/_stress.brute")"
            fi
        fi
        if (( i % 200 == 0 )); then
            echo -ne "\r  ... $i/$STRESS_COUNT"
        fi
    done
    echo -ne "\r"
    if [[ $mismatch -eq 0 ]]; then
        pass "All $STRESS_COUNT tests match"
    else
        fail "$mismatch/$STRESS_COUNT mismatches"
    fi
else
    warn "Skipped (missing acc, brute, or gen)"
fi

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}All checks passed.${NC}"
    echo "Next: python -m polyup $(basename "$PROBLEM_DIR")"
else
    echo -e "${RED}${BOLD}$FAILURES check(s) failed.${NC}"
    echo "Fix locally, then re-run ./verify.sh $PROBLEM_DIR"
    echo "See docs/workflow.md for how to prompt the generator to patch a component."
    exit 1
fi
