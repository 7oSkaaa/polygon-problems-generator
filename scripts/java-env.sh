# Locate a real JDK for verify.sh (Polygon solutions use java21).
# Source this file; it sets JAVA_HOME, JAVAC, and JAVA when a working javac is found.
# macOS /usr/bin/javac is a stub and is rejected: it exists but cannot compile.

_polyup_javac_works() {
    local bin="$1"
    [[ -n "$bin" && -x "$bin" ]] || return 1
    "$bin" -version >/dev/null 2>&1
}

_polyup_use_home() {
    local home="$1"
    [[ -n "$home" ]] || return 1
    if _polyup_javac_works "$home/bin/javac"; then
        export JAVA_HOME="$home"
        export JAVAC="$home/bin/javac"
        export JAVA="$home/bin/java"
        return 0
    fi
    return 1
}

_polyup_pick_jdk() {
    local requested="${JAVA_HOME:-}"
    unset JAVAC JAVA

    if [[ -n "$requested" ]]; then
        _polyup_use_home "$requested" && return 0
    fi

    local prefix=""
    if command -v brew >/dev/null 2>&1; then
        prefix="$(brew --prefix openjdk@21 2>/dev/null || true)"
        if [[ -n "$prefix" ]]; then
            _polyup_use_home "$prefix/libexec/openjdk.jdk/Contents/Home" && return 0
            _polyup_use_home "$prefix" && return 0
        fi
        prefix="$(brew --prefix openjdk 2>/dev/null || true)"
        if [[ -n "$prefix" ]]; then
            _polyup_use_home "$prefix/libexec/openjdk.jdk/Contents/Home" && return 0
            _polyup_use_home "$prefix" && return 0
        fi
    fi

    local home
    for home in \
        /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
        /usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
        /opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home \
        /usr/local/opt/openjdk/libexec/openjdk.jdk/Contents/Home \
        /usr/lib/jvm/java-21-openjdk \
        /usr/lib/jvm/java-21-openjdk-amd64 \
        /usr/lib/jvm/temurin-21-jdk; do
        _polyup_use_home "$home" && return 0
    done

    if [[ -x /usr/libexec/java_home ]]; then
        home="$(/usr/libexec/java_home -v 21 2>/dev/null || true)"
        _polyup_use_home "$home" && return 0
        home="$(/usr/libexec/java_home 2>/dev/null || true)"
        _polyup_use_home "$home" && return 0
    fi

    local javac_bin
    javac_bin="$(command -v javac 2>/dev/null || true)"
    if _polyup_javac_works "$javac_bin"; then
        export JAVAC="$javac_bin"
        export JAVA="$(command -v java 2>/dev/null || true)"
        return 0
    fi

    return 1
}

_polyup_pick_jdk || true
unset -f _polyup_javac_works _polyup_use_home _polyup_pick_jdk
