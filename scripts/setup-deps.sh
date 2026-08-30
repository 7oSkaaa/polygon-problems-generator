#!/usr/bin/env bash
# Install local toolchain for ./verify.sh: g++ (C++17) and a real JDK 21 (javac).
# Usage:
#   ./scripts/setup-deps.sh          # install missing pieces
#   ./scripts/setup-deps.sh --check  # only report what is missing (exit 1 if incomplete)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=java-env.sh
source "$ROOT/scripts/java-env.sh"

CHECK_ONLY=false
if [[ "${1:-}" == "--check" ]]; then
    CHECK_ONLY=true
fi

have_gxx=false
if command -v g++ >/dev/null 2>&1 && g++ -dumpversion >/dev/null 2>&1; then
    have_gxx=true
fi

have_java=false
if [[ -n "${JAVAC:-}" ]]; then
    have_java=true
fi

echo "g++:  $(if $have_gxx; then g++ --version | head -1; else echo missing; fi)"
echo "java: $(if $have_java; then "$JAVAC" -version 2>&1 | head -1; else echo 'missing (macOS stub javac does not count)'; fi)"

if $have_gxx && $have_java; then
    echo "Toolchain OK (C++17 + JDK for javac)."
    exit 0
fi

if $CHECK_ONLY; then
    echo "Missing tools. Install with: ./scripts/setup-deps.sh" >&2
    exit 1
fi

os="$(uname -s)"

install_java_macos() {
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew is required to install JDK 21 on macOS." >&2
        echo "Install it from https://brew.sh then re-run ./scripts/setup-deps.sh" >&2
        exit 1
    fi
    echo "Installing OpenJDK 21 via Homebrew..."
    brew install openjdk@21
}

install_java_linux() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "Installing OpenJDK 21 via apt..."
        sudo apt-get update
        sudo apt-get install -y openjdk-21-jdk
        return
    fi
    if command -v dnf >/dev/null 2>&1; then
        echo "Installing OpenJDK 21 via dnf..."
        sudo dnf install -y java-21-openjdk-devel
        return
    fi
    if command -v pacman >/dev/null 2>&1; then
        echo "Installing OpenJDK 21 via pacman..."
        sudo pacman -S --needed --noconfirm jdk21-openjdk
        return
    fi
    echo "No supported package manager found. Install a JDK 21 (Temurin/OpenJDK) so javac works." >&2
    exit 1
}

if ! $have_gxx; then
    case "$os" in
        Darwin)
            echo "g++ is missing. Install Apple Command Line Tools:" >&2
            echo "  xcode-select --install" >&2
            exit 1
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update
                sudo apt-get install -y g++
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y gcc-c++
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -S --needed --noconfirm gcc
            else
                echo "Install a C++17 compiler (g++) and re-run." >&2
                exit 1
            fi
            ;;
        *)
            echo "Unsupported OS for automatic g++ install: $os" >&2
            exit 1
            ;;
    esac
fi

if ! $have_java; then
    case "$os" in
        Darwin) install_java_macos ;;
        Linux) install_java_linux ;;
        *)
            echo "Unsupported OS for automatic JDK install: $os" >&2
            echo "Install JDK 21 and set JAVA_HOME, or put javac on PATH." >&2
            exit 1
            ;;
    esac
    # shellcheck source=java-env.sh
    source "$ROOT/scripts/java-env.sh"
fi

if [[ -z "${JAVAC:-}" ]]; then
    echo "JDK 21 was installed but javac still is not visible." >&2
    echo "Set JAVA_HOME to the JDK home (the directory that contains bin/javac)." >&2
    exit 1
fi

echo "Using $JAVAC ($("$JAVAC" -version 2>&1))"
echo "verify.sh will pick this up automatically. No need to change PATH."
