# skillmd-format-reference.md

# SKILL.md Format Reference

**This is a reference document, not an authoring guide.** It distills the SKILL.md file format as defined across the Agent Skills open standard and platform-specific implementations (Claude Code, Codex CLI, GitHub Copilot) into a single source. It should be updated as the standard and platform implementations evolve.

For SkillShelf-specific conventions, quality standards, and skill writing guidance, see [skill-authoring-guide.md](skill-authoring-guide.md).

Last verified: February 22, 2026

This document covers two layers: the **open standard** (the canonical, cross-platform specification maintained at agentskills.io) and **platform extensions** (fields and behaviors added by individual implementations). Where a detail comes from only one layer, the source is noted.

---

## 1. File and directory structure

### Required files

Every skill is a directory containing exactly one file named `SKILL.md` (case-sensitive) at the directory root. No other files are required.

```
skill-name/
└── SKILL.md
```

Source: agentskills.io/specification

### Optional directories

Three directory names are defined by the open standard:

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Executable code (Python, Bash, JavaScript). Agents may run these without loading their source into context. |
| `references/` | Documentation loaded on demand into context (e.g., `REFERENCE.md`, `FORMS.md`, domain-specific files). |
| `assets/` | Static resources not loaded into context but used in output (templates, images, data files, schemas). |

Two additional directory names appear in Claude Code documentation but are not part of the open standard:

| Directory | Purpose |
|-----------|---------|
| `templates/` | Template files for Claude to fill in. |
| `examples/` | Example output showing expected format. |

Source: agentskills.io/specification, code.claude.com/docs/en/skills

### Directory naming

The parent directory name **must match** the `name` field in the YAML frontmatter. This is a hard constraint in the open standard. If the `name` field is omitted in Claude Code, the directory name is used as the skill name.

Source: agentskills.io/specification (hard constraint), code.claude.com/docs/en/skills (fallback behavior)

### Discovery paths by platform

**Claude Code:**

| Scope | Path | Notes |
|-------|------|-------|
| Managed (enterprise) | Deployed via managed settings | Highest priority |
| Personal (user) | `~/.claude/skills/<skill-name>/SKILL.md` | Available across all projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | Shared with team via git |
| Nested/monorepo | `packages/<name>/.claude/skills/<skill-name>/SKILL.md` | Auto-discovered in subdirectories |
| Plugin | `skills/<skill-name>/SKILL.md` within plugin root | Namespaced as `plugin-name:skill-name` |
| Additional directories | `.claude/skills/` within directories added via `--add-dir` | Supports live change detection |

Legacy path: `.claude/commands/<name>.md` files continue to work and support the same frontmatter. If a skill and a command share the same name, the skill takes precedence.

Source: code.claude.com/docs/en/skills, code.claude.com/docs/en/plugins

**OpenAI Codex CLI** (in precedence order, high to low):

| Scope | Path |
|-------|------|
| Repo (CWD) | `$CWD/.codex/skills/<skill-name>/SKILL.md` |
| Repo (parent) | `$CWD/../.codex/skills/` up to repo root |
| Repo (root) | `$REPO_ROOT/.codex/skills/` |
| User | `~/.codex/skills/<skill-name>/SKILL.md` |
| Admin | `/etc/codex/skills/<skill-name>/SKILL.md` |
| System (bundled) | Bundled with Codex installation |

Source: developers.openai.com/codex/skills/

**GitHub Copilot:**

| Scope | Path |
|-------|------|
| Project | `.github/skills/<skill-name>/SKILL.md` |
| Compatibility | Also recognizes `.claude/skills/` |

Source: code.visualstudio.com/docs/copilot/customization/agent-skills

---

## 2. YAML frontmatter specification

The SKILL.md file begins with YAML frontmatter delimited by `---` on the first line and a closing `---` before the Markdown body.

### Open standard fields

These fields are defined by the agentskills.io specification and are expected to be supported by all conforming implementations.

| Field | Required | Type | Constraints | Description |
|-------|----------|------|-------------|-------------|
| `name` | Yes | string | 1 to 64 characters. Unicode lowercase alphanumeric and hyphens only (`a-z`, `0-9`, `-`). Must not start or end with `-`. Must not contain consecutive hyphens (`--`). Must match parent directory name. | Skill identifier. Becomes the slash command or invocation name. |
| `description` | Yes | string | 1 to 1024 characters. Non-empty. | What the skill does and when to use it. Used by agents for discovery and task matching. |
| `license` | No | string | No stated length limit. | License name or reference to a bundled license file (e.g., `Apache-2.0` or `Proprietary. LICENSE.txt has complete terms`). |
| `compatibility` | No | string | 1 to 500 characters if provided. | Environment requirements: intended product, required system packages, network access needs. Most skills do not need this. |
| `metadata` | No | map (string to string) | Arbitrary key-value pairs. | Additional properties not defined by the spec. Use reasonably unique key names to avoid conflicts. |
| `allowed-tools` | No | string | Space-delimited list. | Pre-approved tools the skill may use. **Marked as experimental.** Support varies between implementations. |

Source: agentskills.io/specification

**Note on "required" vs. Claude Code behavior:** The open standard marks `name` and `description` as required. Claude Code documentation states "All fields are optional. Only `description` is recommended so Claude knows when to use the skill." In Claude Code, omitting `name` causes the directory name to be used instead; omitting `description` means the skill will not be discoverable by the model. Both fields are effectively required for a functional skill.

Source: code.claude.com/docs/en/skills (the "all optional" statement), docs.claude.com/en/docs/agents-and-tools/agent-skills/overview (the "required" statement)

### Claude Code extension fields

These fields are specific to Claude Code and are not part of the open standard.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `disable-model-invocation` | boolean | `false` (omitted) | When `true`, only the user can invoke the skill via `/skill-name`. Claude cannot auto-trigger it. Also removes the skill from Claude's context entirely at startup (the description is not pre-loaded). Use for workflows with side effects. |
| `user-invocable` | boolean | `true` (omitted) | When `false`, the skill does not appear in the user's slash command menu. Claude can still discover and invoke it. Controls menu visibility only, not Skill tool access. |
| `context` | string | (none) | When set to `fork`, the skill runs in isolation as a subagent. The skill content becomes the prompt that drives the subagent. The subagent has no access to conversation history. Only makes sense for skills with explicit task instructions, not reference-only content. |
| `agent` | string | `general-purpose` | Specifies which subagent configuration to use when `context: fork` is set. Built-in values: `Explore`, `Plan`, `general-purpose`. Also accepts any custom subagent name from `.claude/agents/`. |
| `hooks` | object | (none) | Defines hooks scoped to the skill's lifetime (PreToolUse, PostToolUse, Stop). Same format as settings-based hooks. Automatically cleaned up when the skill finishes. Supports `once: true` option. |
| `memory` | string | (none) | Gives the subagent (when used with `context: fork`) a persistent directory that survives across conversations. Documented value: `user`. |
| `argument-hint` | string | (none) | Provides hint text for arguments in slash command completion UI. |

Source: code.claude.com/docs/en/skills, code.claude.com/docs/en/sub-agents, docs.claude.com/en/release-notes/claude-code

### Claude Code name field additional constraints

Beyond the open standard's name rules, Claude Code adds:

- Cannot contain XML tags
- **Cannot contain the reserved words "anthropic" or "claude"** (e.g., `anthropic-helper` and `claude-tools` are invalid)

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices, docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

### Claude Code description field additional constraints

- Cannot contain XML tags
- Should be written in third person (e.g., "Processes Excel files" not "I can help you process Excel files"). The description is injected into the system prompt.

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Codex CLI extension fields

Codex CLI supports the open standard fields. Additionally:

- `metadata.short-description`: Used for user-facing display in the Codex app.
- An optional `agents/openai.yaml` file (separate from SKILL.md) provides UI metadata, invocation policy, and tool dependency declarations specific to the Codex platform.

Source: developers.openai.com/codex/skills/

### Fields read at discovery time vs. activation time

| Timing | What is read |
|--------|-------------|
| Discovery (startup) | `name` and `description` from YAML frontmatter of all installed skills. Approximately 100 tokens per skill. |
| Activation (on trigger) | Full SKILL.md body (frontmatter + Markdown). All frontmatter fields are processed at this point. |
| Execution (as needed) | Supporting files in `scripts/`, `references/`, `assets/`, etc. |

**Exception:** When `disable-model-invocation: true` is set (Claude Code), neither name nor description is loaded at startup. The skill is invisible to Claude until the user manually invokes it.

**Exception:** When skills are listed in a subagent's `skills:` field (Claude Code), the full skill content is injected into the subagent's context at startup, not loaded on demand.

Source: agentskills.io/specification, agentskills.io/what-are-skills, docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

---

## 3. Markdown body specification

### Content

The Markdown body follows the closing `---` of the YAML frontmatter. There are no format restrictions on the body. It may contain any valid Markdown. The body holds the instructions agents follow when the skill is activated.

Two content categories are recognized in Claude Code documentation:

- **Reference content:** Conventions, patterns, style guides, domain knowledge. Runs inline with the current conversation context.
- **Task content:** Step-by-step instructions for specific actions (deployments, commits, code generation). Often paired with `disable-model-invocation: true`.

Source: agentskills.io/specification, code.claude.com/docs/en/skills

### Size guidelines

| Metric | Value | Type |
|--------|-------|------|
| SKILL.md body length | Under 500 lines | **Guideline**, not a hard limit. Exact wording: "Keep SKILL.md body under 500 lines for optimal performance." |
| Instructions token target | Under 5,000 tokens | **Guideline** from the open standard spec ("< 5000 tokens recommended"). |

There is no documented hard limit on SKILL.md body length. Exceeding 500 lines may degrade performance because the full body is loaded into the context window on activation.

Source: agentskills.io/specification, docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### How the body is loaded at runtime

When a skill is activated, the agent reads the full SKILL.md body into its context window. In filesystem-based agents (Claude Code, Codex CLI), this happens via a shell command (e.g., `cat /path/to/skill/SKILL.md`). The agent then follows the instructions in the body, optionally loading referenced files or running scripts as needed.

Source: agentskills.io/integrate-skills, docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

### References to supporting files

Use relative paths from the skill root directory:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

**Guideline:** Keep file references one level deep from SKILL.md. Deeply nested reference chains (file A references file B which references file C) may result in partial reads.

Source: agentskills.io/specification, docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Special syntax (Claude Code only)

**`$ARGUMENTS` placeholder:** When a user invokes `/skill-name some text`, the string "some text" replaces `$ARGUMENTS` in the SKILL.md body. Positional arguments are also available as `$0`, `$1`, `$2`, etc. If the skill body does not contain `$ARGUMENTS`, Claude Code automatically appends `ARGUMENTS: <value>` at the end.

**`!` backtick preprocessing:** The syntax `` !`command` `` runs a shell command before the skill content is sent to the model. The command output replaces the placeholder inline. This is preprocessing, not model-executed code. The model only sees the final rendered output.

Example:
```markdown
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
```

**`ultrathink` keyword:** Including the word "ultrathink" anywhere in the skill body enables extended thinking mode for that skill invocation.

Source: code.claude.com/docs/en/skills

### File path convention

Always use forward slashes in file paths, even on Windows. `scripts/helper.py` is correct; `scripts\helper.py` is not.

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

---

## 4. Supporting file types

### `scripts/`

Contains executable code. Agents run these scripts via shell commands and receive only the output. The script source code does not enter the context window. This makes scripts token-efficient for deterministic operations.

- Scripts should be self-contained or clearly document dependencies.
- Scripts should include helpful error messages and handle edge cases.
- Scripts need execute permissions (`chmod +x`).
- Supported languages depend on the runtime environment (commonly Python, Bash, JavaScript).
- In SKILL.md, instruct the agent to run the script rather than read it.

Source: agentskills.io/specification, code.claude.com/docs/en/skills

### `references/`

Contains additional documentation loaded on demand into context. Files are read (not executed) when the agent determines they are needed based on the instructions in SKILL.md.

- Keep individual reference files focused; smaller files mean less context usage.
- For files longer than approximately 100 lines, include a table of contents.
- For files larger than approximately 10,000 words, include grep search patterns in SKILL.md so the agent can search rather than read the entire file.
- Avoid duplicating information between SKILL.md and reference files.

Source: agentskills.io/specification, docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### `assets/`

Contains static resources that are not loaded into context but are used in outputs or as inputs to scripts. Examples: document templates, images, data files, lookup tables, schemas, fonts.

Source: agentskills.io/specification

### `templates/` and `examples/` (Claude Code convention)

These directories appear in Claude Code documentation examples but are not defined in the open standard. `templates/` holds template files for the agent to fill in. `examples/` holds example output showing expected format. Their contents are read on demand, similar to `references/`.

Source: code.claude.com/docs/en/skills

### Summary: what gets executed vs. read vs. used in output

| Directory | Executed | Read into context | Used in output |
|-----------|----------|-------------------|----------------|
| `scripts/` | Yes (output only enters context) | No (source code stays out of context) | Indirectly (via output) |
| `references/` | No | Yes (on demand) | No |
| `assets/` | No | No | Yes (copied, referenced, or used by scripts) |
| `templates/` | No | Yes (on demand) | Yes (filled in by agent) |
| `examples/` | No | Yes (on demand) | No (used as reference for expected format) |

---

## 5. Discovery and activation lifecycle

### Phase 1: Discovery (at startup)

The agent scans all configured skill directories. For each valid skill directory (containing a `SKILL.md` with valid frontmatter), the agent parses only the YAML frontmatter and extracts `name` and `description`.

These metadata entries are injected into the system prompt. For Claude models, the recommended format uses XML:

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files...</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

Approximate cost: ~100 tokens per skill (~50 to 100 tokens per skill for metadata).

Source: agentskills.io/integrate-skills, agentskills.io/what-are-skills

### Character budget for skill metadata (Claude Code)

When many skills are installed, their combined metadata may exceed the available character budget. Claude Code documentation references a budget that scales dynamically at **2% of the context window**, with a fallback of **16,000 characters**. The environment variable `SLASH_COMMAND_TOOL_CHAR_BUDGET` can override this limit. When the budget is exceeded, some skills are excluded from the system prompt. Run `/context` in Claude Code to check for warnings about excluded skills.

**Caveat:** The 2% / 16,000 character figure appears in some versions of the Claude Code documentation but was not consistently present across all fetched pages. Earlier documentation referenced 15,000 characters. Treat this as an implementation detail that may change.

Source: code.claude.com/docs/en/skills (referenced in some page versions)

### Phase 2: Activation (on trigger)

Activation occurs when:

- **User invocation:** The user types `/skill-name` (Claude Code) or `$skill-name` (Codex CLI).
- **Model invocation:** The agent determines that a user request matches a skill's description and decides to invoke it. In Claude Code, the user sees a confirmation prompt before the full SKILL.md is loaded.

On activation, the agent reads the full SKILL.md file (frontmatter and body) into context. All frontmatter fields are processed at this point.

Source: agentskills.io/what-are-skills, code.claude.com/docs/en/skills

### Phase 3: Execution (as needed)

During execution, the agent follows the instructions in the SKILL.md body. It loads supporting files (references, templates, examples) and runs scripts only when the instructions call for them or the task requires them. This on-demand loading is the third level of progressive disclosure.

Source: agentskills.io/specification, docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

### Lifecycle summary table

| Phase | When | What is loaded | Token cost |
|-------|------|---------------|------------|
| Discovery | Agent startup | `name` and `description` from all skills | ~100 tokens per skill |
| Activation | User or model triggers skill | Full SKILL.md body | Under 5,000 tokens (guideline) |
| Execution | During task performance | Files in `scripts/`, `references/`, `assets/` as needed | Variable; scripts contribute only output |

---

## 6. Cross-platform compatibility

### The open standard

The Agent Skills format was originally developed by Anthropic, released as an open standard on December 18, 2025, and is maintained at agentskills.io under the `agentskills/agentskills` GitHub organization. Code is licensed under Apache 2.0; documentation under CC-BY-4.0. The standard is described as open to contributions from the broader ecosystem.

Source: agentskills.io, github.com/agentskills/agentskills

### Platforms with documented SKILL.md support

As of February 2026, the following platforms have documented SKILL.md support:

- **Claude Code** (Anthropic): Full support with extensions. Originator of the format.
- **Claude.ai** (Anthropic): Pre-built and custom skills via ZIP upload.
- **Claude API** (Anthropic): Skills via API with beta headers.
- **Claude Agent SDK** (Anthropic): Filesystem-based custom skills.
- **OpenAI Codex CLI, IDE extension, and Codex app** (OpenAI): Full support of the open standard.
- **GitHub Copilot** (Microsoft/GitHub): Support in VS Code, CLI, and coding agent.
- **Cursor**, **Amp**, **Letta**, **Goose** (Block), **OpenCode**, **Windsurf**, **Gemini CLI** (Google), **Roo Code**, **Trae**: Listed as adopters on agentskills.io.

Source: agentskills.io (homepage adopter list), developers.openai.com/codex/skills/, code.visualstudio.com/docs/copilot/customization/agent-skills

### What "open standard" means in practice

The open standard defines the minimal, portable subset: YAML frontmatter with `name`, `description`, and optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`), plus the directory structure (`scripts/`, `references/`, `assets/`). A skill conforming to only this subset should work across all adopting platforms, with the caveat that `allowed-tools` is marked experimental and support varies.

Each platform adds its own extensions. A skill using Claude Code's `context: fork` or `disable-model-invocation` will be silently ignored or partially supported on other platforms. A skill using Codex's `agents/openai.yaml` will have that file ignored on Claude Code.

There is no formal versioning of the specification. The spec has been described as intentionally minimal ("deliciously tiny") to allow platform-specific extensions without breaking compatibility.

Source: agentskills.io/specification, github.com/agentskills/agentskills

### Key behavioral differences across platforms

| Feature | Claude Code | Codex CLI | GitHub Copilot |
|---------|-------------|-----------|----------------|
| Skill directory prefix | `.claude/skills/` | `.codex/skills/` | `.github/skills/` (also reads `.claude/skills/`) |
| User invocation syntax | `/skill-name` | `$skill-name` or `/skills` | `/skills` or `$` mention |
| Model auto-invocation | Yes (unless `disable-model-invocation: true`) | Yes (unless `allow_implicit_invocation: false` in config) | Yes |
| `allowed-tools` support | Yes (native, Claude Code only) | Experimental | Undocumented |
| `context: fork` support | Yes | No (Claude Code extension) | No |
| `disable-model-invocation` | Yes | No (uses config.toml instead) | No |
| Admin-level skill path | No | `/etc/codex/skills/` | No |
| Plugin/marketplace skills | Yes (plugin system) | Yes (`$skill-installer`) | Yes (VS Code extension contribution point) |
| Live change detection | Yes (for `--add-dir` directories) | Yes (file watcher) | Undocumented |

Source: code.claude.com/docs/en/skills, developers.openai.com/codex/skills/, code.visualstudio.com/docs/copilot/customization/agent-skills

### Runtime environment differences (Anthropic surfaces)

| Surface | Network access | Package installation |
|---------|---------------|---------------------|
| Claude.ai | Yes (npm, PyPI, GitHub) | Yes |
| Claude API | **No network access** | **No runtime installation** |
| Claude Code | Full network access | Yes (local installation recommended) |

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/overview, docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

---

## 7. Installation and distribution paths

### Claude Code

- **Personal:** Create directory manually at `~/.claude/skills/<skill-name>/SKILL.md`.
- **Project:** Create at `.claude/skills/<skill-name>/SKILL.md` and commit to version control. Team members receive skills on `git pull`.
- **Plugin:** Package skills in a plugin's `skills/` directory. Install via `/plugin marketplace add <publisher>/<repo>`.
- **Managed/enterprise:** Deploy organization-wide through managed settings.
- **Ask Claude:** Prompt Claude Code with "Create a Skill that captures this pattern." Claude understands the format natively.

Source: code.claude.com/docs/en/skills, code.claude.com/docs/en/plugins

### Claude.ai (web)

Upload custom skills as ZIP files through Settings > Features. The ZIP must contain a top-level folder whose name matches the skill name, with `SKILL.md` at the root of that folder. Available on Pro, Max, Team, and Enterprise plans with code execution enabled. Custom skills are individual to each user (not shared organization-wide and cannot be centrally managed by admins).

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

### Claude API

Upload via the `/v1/skills` endpoint using multipart form data. All files must be in the same top-level directory and must include a `SKILL.md`. Requires beta headers: `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14`. Skills created via API are shared organization-wide. Supports versioning by Unix epoch timestamp. Up to **8 skills per API request**.

Source: docs.claude.com/en/api/skills-guide, docs.claude.com/en/api/skills/create-skill

### Claude Agent SDK

Filesystem-based only. Must configure `settingSources` to include `'user'` and/or `'project'`. Must include `"Skill"` in `allowed_tools`. The `allowed-tools` frontmatter field is **not supported** in the SDK; use the SDK's own `allowedTools` option instead.

Source: docs.claude.com/en/docs/agent-sdk/skills

### OpenAI Codex CLI

- **User:** Place in `~/.codex/skills/<skill-name>/SKILL.md`.
- **Project/repo:** Place in `.codex/skills/` at or above the working directory (up to repo root).
- **Admin:** Place in `/etc/codex/skills/`.
- **Installer:** Use the built-in `$skill-installer` skill to install from GitHub repositories.

Source: developers.openai.com/codex/skills/

---

## 8. Validation rules

### Rules that prevent a skill from loading

The following conditions will cause a skill to fail to load or be rejected by validation:

**YAML syntax errors:**
- Missing opening `---` on line 1.
- Missing closing `---` before Markdown content.
- Invalid YAML syntax (e.g., tabs instead of spaces, incorrect indentation, unquoted strings with special characters that break YAML parsing).

**Name field violations (open standard):**
- Length outside 1 to 64 characters.
- Contains uppercase letters.
- Contains characters other than lowercase alphanumeric and hyphens.
- Starts or ends with a hyphen.
- Contains consecutive hyphens (`--`).
- Does not match the parent directory name.

**Name field violations (Claude Code additional):**
- Contains XML tags.
- Contains the reserved words "anthropic" or "claude".

**Description field violations:**
- Empty string (zero characters).
- Length exceeds 1024 characters.
- Contains XML tags (Claude Code).

**Compatibility field violation (if provided):**
- Length exceeds 500 characters.

**File structure violations:**
- No file named `SKILL.md` in the skill directory.
- `SKILL.md` file does not begin with valid YAML frontmatter.

Source: agentskills.io/specification, docs.claude.com/en/docs/agents-and-tools/agent-skills/overview, docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Known edge cases from changelogs

- A bare number for the `name` field (e.g., `name: 3000`) previously caused a crash. This has been fixed; the value is coerced to a string.
- YAML sequence syntax in the `argument-hint` field (e.g., `[topic: foo | bar]`) previously caused a React crash. This has been fixed; the value is coerced to a string.

Source: docs.claude.com/en/release-notes/claude-code

### Validation tooling

The `skills-ref` reference library (Python, from the `agentskills/agentskills` repository) provides a CLI validator:

```
skills-ref validate ./my-skill
```

This checks YAML frontmatter validity and naming convention compliance.

In Claude Code, run `claude --debug` to see skill loading errors.

Source: agentskills.io/specification, code.claude.com/docs/en/skills

### Guidelines vs. hard constraints summary

| Rule | Hard constraint or guideline |
|------|------------------------------|
| `name` max 64 characters | Hard constraint |
| `name` lowercase alphanumeric and hyphens only | Hard constraint |
| `name` no leading/trailing/consecutive hyphens | Hard constraint |
| `name` must match directory name | Hard constraint (open standard); fallback behavior in Claude Code |
| `name` no reserved words "anthropic", "claude" | Hard constraint (Claude Code only) |
| `description` max 1024 characters | Hard constraint |
| `description` non-empty | Hard constraint |
| `compatibility` max 500 characters | Hard constraint (if field is provided) |
| SKILL.md body under 500 lines | Guideline ("for optimal performance") |
| Instructions under 5,000 tokens | Guideline (open standard recommendation) |
| File references one level deep | Guideline (deeper nesting may cause partial reads) |
| Description in third person | Guideline (Claude Code best practice) |

---

## 9. What NOT to include in a skill

These anti-patterns are documented in official sources:

- **Vague descriptions.** "Helps with documents" or "For files" does not give the agent enough information to match tasks to the skill.
- **Overlapping descriptions across skills.** Two skills with descriptions like "For data analysis" and "For analyzing data" cause confusion during task matching.
- **Too-broad scope.** A single skill called "Document processing" or "Data tools" should be split into focused, single-capability skills.
- **Multiple approaches without a default.** Presenting several options forces the agent to choose. Provide one default approach with an escape hatch.
- **Redundant explanations of common concepts.** The model already knows standard programming concepts, common tools, and general knowledge. Only add context the model does not already have.
- **Windows-style backslash paths.** Always use forward slashes.
- **Deeply nested file references.** Reference files from SKILL.md directly. Do not chain references (file A to file B to file C).
- **Time-sensitive information.** Dates, version numbers, or facts that will become stale reduce skill reliability over time.
- **`context: fork` on reference-only content.** If a skill contains only guidelines (e.g., "use these API conventions") without an actionable task, a forked subagent receives the guidelines but no prompt, and returns without meaningful output.
- **First or second person in descriptions.** Descriptions are injected into the system prompt. Use third person ("Processes Excel files"), not first person ("I can help you process Excel files") or second person ("You can use this to process Excel files").
- **Assuming tools or packages are installed.** Verify availability or document dependencies in the `compatibility` field.
- **Magic numbers without justification.** All constants in scripts should be explained.
- **Punting errors to the model.** Handle error conditions in scripts rather than producing unhelpful error output for the model to interpret.
- **Specialized workflows in CLAUDE.md.** CLAUDE.md loads every session; skills load on demand. Move workflow-specific content into skills.
- **Relying on `user-invocable: false` to prevent model invocation.** This field only controls menu visibility. Use `disable-model-invocation: true` to actually prevent model invocation.

Source: docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices, code.claude.com/docs/en/skills, code.claude.com/docs/en/best-practices

---

## Ambiguous or undocumented areas

The following areas are not fully specified or are inconsistent across official sources:

1. **No formal spec version number.** The agentskills.io specification has no version identifier. There are no releases published on the `agentskills/agentskills` GitHub repository.

2. **`allowed-tools` is experimental.** The open standard marks this field as experimental with the note "Support for this field may vary between agent implementations." No formal grammar for tool patterns (e.g., `Bash(git:*)` vs. `Read`) is defined in the open standard.

3. **Character budget specifics.** The 2% of context window / 16,000 character fallback for skill description budgets is referenced in some Claude Code documentation but was not consistently present across all fetched pages. Treat as an implementation detail.

4. **`metadata` field key constraints.** The open standard says "string keys to string values" but does not specify key naming rules, reserved keys, or maximum counts.

5. **Body content when empty.** The specification says the Markdown body may be empty ("typically contains instructions") but does not specify behavior when the body is blank.

6. **Interaction between `allowed-tools` frontmatter and platform permission systems.** The Claude Code docs state that tools listed in `allowed-tools` are granted "without per-use approval," but the relationship to the broader permission model (deny lists, `Skill(name)` permission syntax) is not fully documented.

7. **`templates/` and `examples/` directories.** These appear in Claude Code documentation examples but are not defined in the open standard. Their behavior relative to `references/` and `assets/` is inferred from context rather than formally specified.

8. **Cross-platform behavior of platform-specific fields.** Whether non-standard frontmatter fields (e.g., Claude Code's `context: fork`) cause errors or are silently ignored on other platforms is not documented in the open standard.

9. **`memory` field scope and behavior.** Referenced in subagent documentation but its exact behavior when used in skill frontmatter (outside the subagent `skills:` field) is not clearly documented.

---

## Sources consulted

| Source | URL |
|--------|-----|
| Agent Skills Specification (canonical) | https://agentskills.io/specification |
| Agent Skills: What are skills? | https://agentskills.io/what-are-skills |
| Agent Skills: Integrate skills | https://agentskills.io/integrate-skills |
| Agent Skills GitHub (spec source) | https://github.com/agentskills/agentskills |
| Anthropic Skills GitHub (examples) | https://github.com/anthropics/skills |
| Claude Code: Agent Skills | https://code.claude.com/docs/en/skills |
| Claude Code: Best Practices | https://code.claude.com/docs/en/best-practices |
| Claude Code: Plugins | https://code.claude.com/docs/en/plugins |
| Claude Code: Subagents | https://code.claude.com/docs/en/sub-agents |
| Claude Code: Settings | https://code.claude.com/docs/en/settings |
| Claude Docs: Agent Skills Overview | https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview |
| Claude Docs: Best Practices | https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices |
| Claude Docs: Skills API Guide | https://docs.claude.com/en/api/skills-guide |
| Claude Docs: Agent SDK Skills | https://docs.claude.com/en/docs/agent-sdk/skills |
| Claude Code Release Notes | https://docs.claude.com/en/release-notes/claude-code |
| OpenAI Codex CLI: Skills | https://developers.openai.com/codex/skills/ |
| OpenAI Codex Changelog | https://developers.openai.com/codex/changelog/ |
| OpenAI Skills GitHub | https://github.com/openai/skills |
| GitHub Copilot: Agent Skills | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| Anthropic Engineering Blog: Agent Skills | https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |