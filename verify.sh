#!/bin/bash
set -euo pipefail

# ── Auto-verify pipeline for a problem folder ────────────────────────────────
# Usage: ./verify.sh problems/<name> [--stress N]
#
# Steps:
#   1. Compile validator, generator, all solutions, checker (if custom)
#   2. Generate tests via generator
#   3. Validate every generated test with the validator
#   4. Run ACC solution to produce expected output
#   5. Run checker (ACC output vs ACC output) as sanity check
#   6. Run WA solution and confirm checker rejects it on at least one test
#   7. Stress test: ACC vs brute on random small inputs
#   8. Report summary

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
header() { echo -e "\n${BOLD}[$1]${NC}"; }

PROBLEM_DIR="${1:?Usage: ./verify.sh problems/<name> [--stress N]}"
PROBLEM_DIR="${PROBLEM_DIR%/}"
STRESS_COUNT=1000

if [[ "${2:-}" == "--stress" ]]; then
    STRESS_COUNT="${3:-1000}"
fi

if [[ ! -d "$PROBLEM_DIR" ]]; then
    echo "Error: $PROBLEM_DIR not found"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TESTLIB="$REPO_ROOT/testlib/testlib.h"
STANDARD_CHECKERS="$REPO_ROOT/testlib/checkers"
CXX="${CXX:-g++}"
CXXFLAGS="-std=c++17 -O2 -I$(dirname "$TESTLIB") -I$HOME/.local/include"
BUILD="$PROBLEM_DIR/.build"
TESTS="$PROBLEM_DIR/.tests"
FAILURES=0

# portable timeout — just run directly; brute may be slow but stress.conf keeps inputs small
if command -v gtimeout &>/dev/null; then
    run_timed() { gtimeout "$@"; }
elif command -v timeout &>/dev/null 2>&1 && timeout --version &>/dev/null 2>&1; then
    run_timed() { timeout "$@"; }
else
    # no timeout available — just run without limit
    run_timed() { shift; "$@"; }
fi

cleanup() {
    rm -rf "$BUILD" "$TESTS"
}
trap cleanup EXIT

mkdir -p "$BUILD" "$TESTS"

echo -e "${BOLD}Verifying: ${PROBLEM_DIR}${NC}"

# ── 1. Detect checker type ───────────────────────────────────────────────────

header "Checker"

CHECKER_SRC="$PROBLEM_DIR/checker.cpp"
CUSTOM_CHECKER=false

if [[ -f "$CHECKER_SRC" ]]; then
    first_line=$(head -1 "$CHECKER_SRC")
    if [[ "$first_line" == "// Use standard checker:"* ]]; then
        CHECKER_NAME=$(echo "$first_line" | sed 's/.*: \([a-z]*\).*/\1/')
        CHECKER_STANDARD_SRC="$STANDARD_CHECKERS/${CHECKER_NAME}.cpp"
        if [[ -f "$CHECKER_STANDARD_SRC" ]]; then
            $CXX $CXXFLAGS -o "$BUILD/checker" "$CHECKER_STANDARD_SRC"
            pass "Standard checker: $CHECKER_NAME"
        else
            fail "Standard checker '$CHECKER_NAME' not found in $STANDARD_CHECKERS"
        fi
    else
        CUSTOM_CHECKER=true
        $CXX $CXXFLAGS -o "$BUILD/checker" "$CHECKER_SRC"
        pass "Custom checker compiled"
    fi
else
    fail "No checker.cpp found"
fi

# ── 2. Compile validator ─────────────────────────────────────────────────────

header "Validator"

VALIDATOR_SRC="$PROBLEM_DIR/validator.cpp"
if [[ -f "$VALIDATOR_SRC" ]]; then
    $CXX $CXXFLAGS -o "$BUILD/validator" "$VALIDATOR_SRC"
    pass "Compiled"
else
    fail "No validator.cpp found"
fi

# ── 3. Compile generator ────────────────────────────────────────────────────

header "Generator"

GEN_SRC=$(find "$PROBLEM_DIR/generators" -name "generator.cpp" 2>/dev/null | head -1)
if [[ -n "$GEN_SRC" ]]; then
    $CXX $CXXFLAGS -o "$BUILD/gen" "$GEN_SRC"
    pass "Compiled"
else
    fail "No generator.cpp found"
fi

# ── 4. Compile solutions ────────────────────────────────────────────────────

header "Solutions"

compile_solution() {
    local src="$1"
    local name=$(basename "$src" .cpp)
    local ext="${src##*.}"

    if [[ "$ext" == "cpp" ]]; then
        $CXX $CXXFLAGS -o "$BUILD/$name" "$src" 2>&1 && pass "$name.cpp" || fail "$name.cpp failed to compile"
    elif [[ "$ext" == "java" ]]; then
        local classname=$(basename "$src" .java)
        if javac --version &>/dev/null; then
            javac -d "$BUILD" "$src" 2>&1 && pass "$classname.java" || fail "$classname.java failed to compile"
        else
            warn "$classname.java skipped (javac not found)"
        fi
    fi
}

for src in "$PROBLEM_DIR/solutions/"*.cpp; do
    [[ -f "$src" ]] && compile_solution "$src"
done

for src in "$PROBLEM_DIR/solutions/"*.java; do
    [[ -f "$src" ]] && compile_solution "$src"
done

# ── 5. Generate tests + validate ────────────────────────────────────────────

header "Test generation + validation"

if [[ -x "$BUILD/gen" && -x "$BUILD/validator" ]]; then
    test_idx=0
    gen_fail=0
    val_fail=0

    # Edge cases
    EDGE_SEEDS=(1 2 3 4 5 6 7 8 9 10)
    for seed in "${EDGE_SEEDS[@]}"; do
        test_idx=$((test_idx + 1))
        if "$BUILD/gen" "$seed" > "$TESTS/test_${test_idx}.in" 2>/dev/null; then
            if ! "$BUILD/validator" < "$TESTS/test_${test_idx}.in" > /dev/null 2>&1; then
                val_fail=$((val_fail + 1))
                [[ $val_fail -le 3 ]] && warn "Validator rejected test seed=$seed"
            fi
        else
            gen_fail=$((gen_fail + 1))
        fi
    done

    if [[ $gen_fail -eq 0 && $val_fail -eq 0 ]]; then
        pass "Generated $test_idx tests, all passed validation"
    elif [[ $val_fail -gt 0 ]]; then
        fail "$val_fail/$test_idx tests rejected by validator"
    fi
    if [[ $gen_fail -gt 0 ]]; then
        fail "$gen_fail/$test_idx tests failed to generate"
    fi
else
    warn "Skipped (missing gen or validator)"
fi

# ── 6. Run ACC on all tests ─────────────────────────────────────────────────

header "ACC solution"

if [[ -x "$BUILD/acc" ]]; then
    acc_fail=0
    for input in "$TESTS"/*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        if ! run_timed 5 "$BUILD/acc" < "$input" > "$TESTS/${base}.ans" 2>/dev/null; then
            acc_fail=$((acc_fail + 1))
        fi
    done
    total=$(ls "$TESTS"/*.in 2>/dev/null | wc -l | tr -d ' ')
    if [[ $acc_fail -eq 0 ]]; then
        pass "Ran on $total tests"
    else
        fail "$acc_fail/$total tests failed or timed out"
    fi
else
    fail "acc binary not found"
fi

# ── 7. Checker sanity: ACC vs ACC ────────────────────────────────────────────

header "Checker sanity (ACC vs ACC)"

if [[ -x "$BUILD/checker" && -x "$BUILD/acc" ]]; then
    chk_fail=0
    for input in "$TESTS"/*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        ans="$TESTS/${base}.ans"
        [[ -f "$ans" ]] || continue
        if ! "$BUILD/checker" "$input" "$TESTS/${base}.ans" "$ans" > /dev/null 2>&1; then
            chk_fail=$((chk_fail + 1))
            [[ $chk_fail -le 3 ]] && warn "Checker rejected ACC output on $base"
        fi
    done
    total=$(ls "$TESTS"/*.ans 2>/dev/null | wc -l | tr -d ' ')
    if [[ $chk_fail -eq 0 ]]; then
        pass "All $total tests accepted"
    else
        fail "$chk_fail/$total tests rejected by checker"
    fi
else
    warn "Skipped (missing checker or acc)"
fi

# ── 8. Java ACC cross-check ─────────────────────────────────────────────────

header "Java ACC cross-check"

JAVA_CLASS=$(find "$BUILD" -name "acc_java.class" 2>/dev/null | head -1)
if [[ -n "$JAVA_CLASS" ]]; then
    java_fail=0
    for input in "$TESTS"/*.in; do
        [[ -f "$input" ]] || continue
        base=$(basename "$input" .in)
        ans="$TESTS/${base}.ans"
        [[ -f "$ans" ]] || continue
        java_out="$TESTS/${base}.java_out"
        if run_timed 10 java -cp "$BUILD" acc_java < "$input" > "$java_out" 2>/dev/null; then
            if ! diff -q "$ans" "$java_out" > /dev/null 2>&1; then
                java_fail=$((java_fail + 1))
                [[ $java_fail -le 3 ]] && warn "Java output differs on $base"
            fi
        else
            java_fail=$((java_fail + 1))
        fi
    done
    total=$(ls "$TESTS"/*.ans 2>/dev/null | wc -l | tr -d ' ')
    if [[ $java_fail -eq 0 ]]; then
        pass "Matches C++ ACC on $total tests"
    else
        fail "Java differs on $java_fail/$total tests"
    fi
else
    warn "Skipped (no acc_java.class)"
fi

# ── 9. WA solution: checker must reject on at least one test ─────────────────

header "WA solution rejection"

if [[ -x "$BUILD/wa" && -x "$BUILD/checker" ]]; then
    wa_rejected=0
    wa_total=0
    for input in "$TESTS"/*.in; do
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

# ── 10. Stress test: ACC vs Brute ────────────────────────────────────────────

header "Stress test (ACC vs Brute, $STRESS_COUNT iterations)"

# Auto-detect stress args from generator source, or use stress.conf override
auto_stress_args() {
    local gen_src="$1"
    [[ -f "$gen_src" ]] || return

    # Parse opt<int>("name", default) lines from generator
    # For each opt with a large default (>= 1000), emit -name <small_value>
    # Cap strategy: values >= 10^6 → 100, values >= 1000 → min(val, 100)
    grep -oE 'opt<int>\("([^"]+)",\s*([^)]+)\)' "$gen_src" | \
    sed -E 's/opt<int>\("([^"]+)",\s*([^)]+)\)/\1 \2/' | \
    while read -r name default_expr; do
        # Evaluate the default: strip number formatting (apostrophes), handle simple expressions
        val=$(echo "$default_expr" | tr -d "'" | tr -d ' ')
        # Skip non-numeric defaults (like rnd.next(...) or -1)
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
    : # use env var as-is
elif [[ -n "$GEN_SRC" ]]; then
    STRESS_GEN_ARGS=$(auto_stress_args "$GEN_SRC")
fi
STRESS_GEN_ARGS="${STRESS_GEN_ARGS:-}"

if [[ -n "$STRESS_GEN_ARGS" ]]; then
    echo -e "  ${YELLOW}→${NC} stress args: $STRESS_GEN_ARGS"
fi

if [[ -x "$BUILD/acc" && -x "$BUILD/brute" && -x "$BUILD/gen" ]]; then
    mismatch=0
    for i in $(seq 1 "$STRESS_COUNT"); do
        "$BUILD/gen" $STRESS_GEN_ARGS "$i" > "$TESTS/_stress.in" 2>/dev/null
        run_timed 5 "$BUILD/acc" < "$TESTS/_stress.in" > "$TESTS/_stress.acc" 2>/dev/null
        run_timed 30 "$BUILD/brute" < "$TESTS/_stress.in" > "$TESTS/_stress.brute" 2>/dev/null || true
        if ! diff -q "$TESTS/_stress.acc" "$TESTS/_stress.brute" > /dev/null 2>&1; then
            mismatch=$((mismatch + 1))
            if [[ $mismatch -le 1 ]]; then
                echo ""
                warn "First mismatch on seed=$i:"
                echo "    Input:    $(cat "$TESTS/_stress.in" | head -3 | tr '\n' ' ')"
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
else
    echo -e "${RED}${BOLD}$FAILURES check(s) failed.${NC}"
    exit 1
fi
