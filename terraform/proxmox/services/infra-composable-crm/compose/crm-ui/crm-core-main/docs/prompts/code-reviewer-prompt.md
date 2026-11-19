# Prompt — Generate a `code-reviewer.md` for any project

Use this prompt with any AI agent to produce a **code review guide** (e.g. `ui-crm-core-agent-code-reviewer.md`) tailored to a specific project. The output documents *how to evaluate code quality*: React Query patterns, file architecture, anti-patterns, TypeScript, performance, and a standardized issue-reporting format with 🔴 / 🟡 / 🟢 severity.

---

## Prompt

> You are a senior staff engineer specialized in code review. Your task is to produce a single Markdown file that serves as the **definitive code-review playbook** for this project. The output is a *reviewer's reference*, not a style guide and not a tutorial.
>
> ### Step 1 — Explore the codebase
> Inspect the repository to ground every rule in real conventions. Read at minimum:
> - `package.json` and lockfile (framework, state, data-fetching, testing libs)
> - Root configs: `tsconfig*.json`, `eslint.config.*`, `vite.config.*`, `vitest.config.*`
> - API / data layer (`lib/api.ts`, `services/`, `hooks/use-*`)
> - Routing entry (`App.tsx`, `main.tsx`, route files)
> - Feature modules to identify naming conventions and module boundaries
> - Existing design-system / style guide doc if one already exists (link to it instead of duplicating visual rules)
>
> Do **not** invent rules. Every pattern, query-key prefix, file path, or limit you cite must reflect the actual repo.
>
> ### Step 2 — Produce the review guide with these sections
> 1. **Front-matter / metadata** — `name`, `description`, `tools` (Read, Grep, Glob), `model`.
> 2. **Role statement** — "You are a senior code reviewer for the {Project} project."
> 3. **Review focus areas** — bullet list scoped to the stack (TypeScript correctness, React patterns, data layer, accessibility, performance, security).
> 4. **Technology Stack** — short table so the reviewer knows the assumed environment.
> 5. **Architecture rules** (most important section)
>    - File / module structure expectations.
>    - **Component size limit** (e.g. 250 lines) with refactor guidance.
>    - **Two-layer data pattern**: raw transport in `lib/api.ts` vs. consumer hooks in `hooks/use-*.ts`. Components must never call the transport layer directly.
>    - **React Query (or equivalent) conventions**: query-key namespacing per module (e.g. `lss-*`), staleness defaults, mandatory invalidation on mutations, optimistic update rules.
>    - **State management**: when to use local state vs. server state vs. URL state.
> 6. **TypeScript rules** — no `any` without justification, prefer `unknown` + narrowing, exhaustive `switch`, discriminated unions for variants, explicit return types on exported functions.
> 7. **React patterns** — controlled vs. uncontrolled, key stability in lists, effect dependencies, memoization only when measured, forbid prop drilling beyond 2 levels (use context or composition).
> 8. **Accessibility** — semantic HTML, label associations, focus management, keyboard nav, ARIA only when necessary, color-contrast deferred to the design-system doc.
> 9. **Performance** — bundle hygiene (no barrel re-exports of heavy modules), lazy routes, image sizing, list virtualization thresholds, avoid re-renders from unstable callbacks/objects.
> 10. **Security** — no secrets in client code, sanitize `dangerouslySetInnerHTML`, validate all external input, never trust client-side role checks, RLS / authz expectations if a backend is present.
> 11. **Testing expectations** — what must have tests (hooks, reducers, critical flows), mocking conventions for the data layer, snapshot policy.
> 12. **Anti-patterns** — two-column ❌/✅ table covering the most common offenses in this codebase.
> 13. **Review process** — ordered steps the reviewer follows: read the diff, map to module, check architecture rules, run static checks mentally, flag issues.
> 14. **Issue reporting format** — every finding must be reported as:
>     ```
>     [SEVERITY] <file>:<line> — <one-line title>
>     Why it matters: ...
>     Suggested fix: ...
>     ```
>     Severity legend:
>     - 🔴 **Critical** — bugs, security issues, data loss, broken contracts. Must fix before merge.
>     - 🟡 **Warning** — maintainability, performance, accessibility regressions. Should fix.
>     - 🟢 **Suggestion** — style, naming, minor refactors. Optional.
>     - ✅ **Positive** — call out exemplary patterns worth repeating.
> 15. **Review checklist** — short pre-merge checklist the reviewer ticks off.
>
> ### Step 3 — Style and constraints
> - Output **one Markdown file**, ready to drop into `docs/`.
> - Tables and bullet lists, no marketing prose, no emoji other than the severity icons.
> - Be specific to this project: cite real file paths, real query-key prefixes, real module names.
> - Stay focused on **code quality**. Do not duplicate visual / design-token rules — link to the project's `style-fixer.md` (or equivalent) instead.
> - Keep it actionable: every rule should be something a reviewer can verify by reading a diff.

---

## How to use

1. Open the target project in your AI tool of choice.
2. Paste the prompt above.
3. Let the agent explore the repo and produce the review guide (e.g. `docs/<project>-code-reviewer.md`).
4. Verify cited paths and conventions match reality; trim anything the project doesn't actually enforce.