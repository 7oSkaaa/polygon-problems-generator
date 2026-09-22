# Getting Started & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:
- [.agents/skills/checker-agent/SKILL.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/checker-agent/SKILL.md)
- [.agents/skills/generator-agent/SKILL.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/generator-agent/SKILL.md)
- [.agents/skills/validator-agent/SKILL.md](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.agents/skills/validator-agent/SKILL.md)
- [.claude/settings.json](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/settings.json)
- [.env.example](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env.example)
- [.githooks/pre-commit](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.githooks/pre-commit)
- [.gitignore](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore)
- [scripts/java-env.sh](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh)
- [scripts/setup-deps.sh](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/setup-deps.sh)

</details>



## Purpose and Scope

This section covers the initial bootstrap procedure for the `polygon-problems-generator` repository. It details environment setup, dependency acquisition for C++17 and Java 21 compilation (`scripts/setup-deps.sh`, `scripts/java-env.sh`) `[[.env:1-5](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env#L1-L5)]`, secrets management via `.env` files `[[.env.example:1-5](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env.example#L1-L5)]`, version control exclusions (`.gitignore`), Model Context Protocol (MCP) server integration for AI assistants (`.claude/settings.json`), and automated configuration synchronization through Git hooks (`.githooks/pre-commit`).

---

## Secrets Management & Environment Variables

To interact with the Polygon API and manage problem packages, the toolchain requires Polygon API credentials. These secrets are configured via a local `.env` file at the repository root, which is parsed by the `polyup` configuration module.

The structure of the environment is defined in `[[.env.example:1-5](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env.example#L1-L5)]`:
- `POLYGON_API_KEY`: The public API key issued by Polygon.
- `POLYGON_API_SECRET`: The corresponding secret key used to sign API requests.
- `POLYGON_DEFAULT_ACCESS` (Optional): Comma-separated user-level mappings (e.g., `alice:WRITE,bob:READ`) granted automatically during problem synchronization.

Because `.env` contains sensitive keys, it is explicitly excluded from version control by `[.gitignore:105-105](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore#L105-L105)`.

```mermaid
graph TD
    EnvExample[".env.example"] -->|"Template for"| EnvFile[".env (Local Secret)"]
    EnvFile -->|"Parsed by"| PolyupConfig["polyup/config.py"]
    PolyupConfig -->|"Signs requests for"| PolygonAPI["Polygon API Client"]

    sub5["Sources: [.env.example:1-4](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env.example#L1-L4), [.gitignore:105-105](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore#L105-L105)"]
end
```
Sources: `[[.env.example:1-5](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.env.example#L1-L5)]`, `[[.gitignore:105-105](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore#L105-L105)]`

---

## Toolchain & JDK 21 Environment Setup

Verification of problem components (such as validators, checkers, generators, and Java solutions) requires a C++17 compiler (`g++`) and a valid Java Development Kit (JDK 21) for `javac` execution. 

### JDK Resolution (`scripts/java-env.sh`)
The script `[scripts/java-env.sh:1-76](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L1-L76)` provides robust environment detection for Java. On macOS, system-provided binaries such as `/usr/bin/javac` are often non-functional stubs; `[scripts/java-env.sh:5-9](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L5-L9)` defines `_polyup_javac_works()` to test actual compilation capability before accepting a JDK path. 

The resolution sequence (`_polyup_pick_jdk`) checks:
1. An explicitly requested `$JAVA_HOME` override `[scripts/java-env.sh:24-29](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L24-L29)`.
2. Homebrew installations of OpenJDK 21 (`/opt/homebrew/opt/openjdk@21`, etc.) `[scripts/java-env.sh:31-43](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L31-L43)`.
3. Standard Linux JVM directories (`/usr/lib/jvm/java-21-openjdk`, `/usr/lib/jvm/temurin-21-jdk`) `[scripts/java-env.sh:46-55](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L46-L55)`.
4. macOS utility `/usr/libexec/java_home` `[scripts/java-env.sh:57-62](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L57-L62)`.

### Dependency Installer (`scripts/setup-deps.sh`)
The installer script `[scripts/setup-deps.sh:1-121](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/setup-deps.sh#L1-L121)` orchestrates toolchain acquisition:
- Sources `[scripts/java-env.sh:10-10](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L10-L10)` to locate existing compilers/runtimes.
- Supports a `--check` flag to verify system readiness without modifying the filesystem (exiting with status `1` if tools are missing).
- Automatically invokes platform-specific package managers (`brew` on macOS; `apt-get`, `dnf`, or `pacman` on Linux) to install `g++` and `openjdk-21-jdk` if they are absent `[scripts/setup-deps.sh:42-112](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/setup-deps.sh#L42-L112)`.

```mermaid
graph TD
    SetupScript["scripts/setup-deps.sh"] -->|"Sources"| JavaEnv["scripts/java-env.sh"]
    JavaEnv -->|"Checks"| JavacCheck["_polyup_javac_works()"]
    JavacCheck -->|"Valid JDK 21 Found"| ExportVars["Export JAVA_HOME, JAVAC, JAVA"]
    JavacCheck -->|"Missing / Stub"| PackageMgr["Package Manager (brew / apt / dnf / pacman)"]
    PackageMgr -->|"Installs"| JDK21["OpenJDK 21 & g++ (C++17)"]

    subSources["Sources: [scripts/java-env.sh:1-76](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L1-L76), [scripts/setup-deps.sh:1-121](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/setup-deps.sh#L1-L121)"]
end
```
Sources: `[[scripts/java-env.sh:1-77](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/java-env.sh#L1-L77)]`, `[[scripts/setup-deps.sh:1-122](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/scripts/setup-deps.sh#L1-L122)]`

---

## Version Control & Repository Exclusions

The repository excludes local build outputs, IDE configurations, temporary caches, and generated problem instances through `[.gitignore:1-199](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore#L1-L199)`. Key exclusion patterns include:
- **Problem Directories**: `problems/`, ensuring that local problem working directories are not accidentally committed to the shared codebase.
- **Python Artifacts**: `__pycache__/`, virtual environments (`.venv/`, `env/`), and package build metadata.
- **C++ Build Outputs**: Object files, static libraries, and compiled binaries (`*.o`, `*.exe`, `*.out`, `compile_commands.json`).
- **Editor Settings**: `.vscode/`, `.idea/`, and system files like `.DS_Store`.

Sources: `[[.gitignore:1-199](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.gitignore#L1-L199)]`

---

## AI Agent Integration & MCP Configuration

To support autonomous AI coding agents (such as Claude, Cursor, and Copilot), the repository utilizes Model Context Protocol (MCP) servers and centralized skill definitions.

### MCP Servers (`.claude/settings.json`)
The configuration file `[.claude/settings.json:1-34](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/settings.json#L1-L34)` registers six specialized MCP server instances (`statement`, `validator`, `checker`, `generator`, `solutions`, and `reviewer`). Each server executes a dedicated Python script located under the `mcps/` directory, giving AI assistants tool-calling capabilities tailored to specific problem components.

### Configuration Synchronization & Git Hooks (`.githooks/pre-commit`)
AI rule files for various editors (`.cursor/rules/`, `.windsurfrules`, `.github/copilot-instructions.md`, `AGENTS.md`, and `.agents/skills/`) are generated automatically from `.claude/shared.md` and `.claude/agents/` via `sync-ai-configs.py`. 

To ensure these rules remain synchronized with source definitions, the pre-commit hook `[.githooks/pre-commit:1-17](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.githooks/pre-commit#L1-L17)` executes the synchronization script before every commit and automatically stages the resulting files:

```mermaid
graph TD
    Commit["git commit"] -->|"Triggers"| PreCommit[".githooks/pre-commit"]
    PreCommit -->|"Executes"| SyncScript["sync-ai-configs.py"]
    SyncScript -->|"Generates"| AICoordinate[".cursor/rules, AGENTS.md, Copilot, Windsurf, Skills"]
    AICoordinate -->|"git add"| StagedFiles["Staged AI Config Files"]

    subSources["Sources: [.githooks/pre-commit:1-17](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.githooks/pre-commit#L1-L17), [.claude/settings.json:1-34](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/settings.json#L1-L34)"]
end
```
Sources: `[[.githooks/pre-commit:1-18](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.githooks/pre-commit#L1-L18)]`, `[[.claude/settings.json:1-34](https://github.com/7oSkaaa/polygon-problems-generator/blob/main/.claude/settings.json#L1-L34)]`
