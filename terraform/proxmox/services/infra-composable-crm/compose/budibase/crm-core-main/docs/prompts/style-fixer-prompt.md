# Prompt — Generate a `style-fixer.md` for any project

Use this prompt with any AI agent (Lovable, Claude, Cursor, ChatGPT, etc.) to produce a **visual design guide** (`style-fixer.md`) for a project. The output documents how the app *looks* — CSS tokens, colors, typography, breakpoints, dark mode, components — and how to fix visual issues or add new UI pieces consistent with the existing design language.

---

## Prompt

> You are a senior UI/Design-System engineer. Your task is to produce a single Markdown file named `style-fixer.md` that serves as the **definitive visual design guide** for this project.
>
> ### Step 1 — Explore the codebase
> Inspect the repository to identify the actual stack and design tokens. Read at minimum:
> - `package.json` (framework, UI libs, icons, state, routing, charts)
> - Global CSS / token files (`index.css`, `globals.css`, `app.css`, `theme.css`, `tokens.*`)
> - Tailwind / UnoCSS / Panda / Stitches config (`tailwind.config.*`, etc.)
> - shadcn / component library config (`components.json`)
> - Layout shell, navigation, theme toggle, and any reusable primitives (`Layout`, `Sidebar`, `PageHeader`, `Badge`, `Card`)
> - Mock data / constants files where ad-hoc color maps live
>
> Do **not** invent values. Every token, class, breakpoint, or path you list must exist in the repo.
>
> ### Step 2 — Produce `style-fixer.md` with these sections
> 1. **Front-matter / metadata** — `name`, `description`, `tools` (Read, Write, Edit, Grep, Glob).
> 2. **Responsibilities** — what this guide covers (CSS bugs, dark mode, responsive, new components, accessibility).
> 3. **Technology Stack** — table mapping Layer → Technology (Framework, Bundler, Styling, Components, Icons, State, Routing, Charts).
> 4. **Design System Reference**
>    - CSS variables table: token → light value → dark value → usage. Include core tokens, semantic status tokens (success/warning/info/destructive), and any sidebar/surface tokens.
>    - Tailwind (or equivalent) class mapping for those tokens.
>    - Border radius scale.
>    - **Critical rule**: always use semantic classes, never raw colors.
> 5. **Color Patterns for Status Badges** — the canonical `bg-{token}/15 text-{token}` (or equivalent) pattern, plus any documented exceptions (e.g. brand-specific palettes) with their light/dark variants.
> 6. **Component Architecture** — annotated `src/` tree highlighting the design-system layer (`components/ui/*`), shared primitives, and feature modules. List the most reused components with example usage snippets.
> 7. **Layout & Responsive Design** — breakpoint table, common responsive patterns (grids, flex headers, padding), sidebar behavior on mobile vs desktop, scrollbar styling.
> 8. **Dark Mode** — how it is toggled and persisted, rules for new components, mandatory `dark:` variants when using palette colors.
> 9. **Interaction Patterns** — keyboard navigation, focus states, minimum touch targets, button sizes.
> 10. **Typography** — font family, base size, heading scale, truncation rules.
> 11. **Common Tasks** — step-by-step recipes: fix responsive issues, fix dark-mode issues, add a new status color, add a new shadcn-style component, add a new page, add a new module section.
> 12. **Anti-Patterns to Avoid** — two-column ❌/✅ table.
> 13. **Utility Reference** — `cn()`, `useIsMobile()`, `useToast()`, or project equivalents, with one-line examples.
> 14. **Checklist for any style change** — semantic tokens, both themes, all breakpoints, focus states, truncation, touch targets, component size limit, `cn()` usage.
>
> ### Step 3 — Style and constraints
> - Output **one Markdown file**, ready to drop into `docs/style-fixer.md`.
> - Use tables, fenced code blocks, and concise bullet lists — no marketing prose.
> - Every value must be grounded in the actual repo; if a token doesn't exist, omit the row instead of guessing.
> - Keep it self-contained: a new contributor should be able to add or fix a UI component using only this document.

---

## How to use

1. Open the target project in your AI tool of choice.
2. Paste the prompt above.
3. Let the agent explore the repo and produce `docs/style-fixer.md`.
4. Review tables against the real `index.css` / `tailwind.config.*` and adjust any drift.