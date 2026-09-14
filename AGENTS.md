# Contribution guidelines

## Scope

These instructions apply to the entire repository. Keep changes focused on the current implementation step, preserve unrelated user changes, and update documentation when behavior changes.

## Branch naming

Use the format:

```text
<type>/<short-kebab-case-description>
```

Use one of these branch types:

- `feat` — new behavior or capability
- `fix` — correction of a defect
- `refactor` — internal restructuring without intended behavior change
- `test` — tests or test infrastructure
- `docs` — documentation-only changes
- `build` — dependencies or packaging
- `ci` — automation or pipeline configuration
- `chore` — maintenance that does not fit the categories above

For the current improvement effort, use:

```text
feat/harden-airflow-etl-pipeline
```

Descriptions should be short, lowercase, and separated with hyphens. Do not use spaces, underscores, issue details, or personal names in branch names.

## Commit messages

Use Conventional Commits:

```text
<type>(<optional-scope>): <imperative description>
```

Examples:

```text
fix(etl): create the staging directory before writing output
feat(etl): add the final staging load task
test(etl): cover fixed-width extraction boundaries
docs(readme): document the local validation workflow
build(deps): constrain Airflow provider versions
```

Rules:

- Use a valid type: `feat`, `fix`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, or `perf`.
- Keep the subject imperative, concise, and lowercase after the colon.
- Do not end the subject with a period.
- Use a scope when it improves clarity; likely scopes here are `etl`, `airflow`, `data`, `tests`, `docs`, `deps`, and `ci`.
- Add a body when the reason, compatibility impact, migration detail, or verification is not obvious from the subject.
- Wrap body lines reasonably and explain what changed and why, not a transcript of every command run.
- Use `BREAKING CHANGE:` in the footer for intentional incompatible behavior, or append `!` to the type/scope when appropriate.

## Step-by-step workflow

Each implementation step should:

1. Make one coherent, reviewable change.
2. Run the most relevant available validation.
3. Summarize the result and any remaining limitations.
4. End with a recommended Conventional Commit message.

Do not combine unrelated fixes into one step or commit. If a step changes runtime behavior, include or update its tests and documentation as part of that step when practical.

